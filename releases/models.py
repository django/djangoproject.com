import datetime
import re
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.validators import RegexValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.version import get_complete_version, get_main_version

from .utils import get_loose_version_tuple


# A version of django.utils.version.get_version() which maps "rc" to "rc"
# (packages generated using setuptools 8+) instead of "c" (older versions of
# setuptools). This naming schemes starts with Django 1.9 and we don't care
# about older release candidates. Safe to use Django's copy of get_version()
# when upgrading this website to use Django 1.10.
def get_version(version=None):
    "Return a PEP 386-compliant version number from VERSION."
    version = get_complete_version(version)

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = {a|b|rc}N - for alpha, beta and rc releases
    main = get_main_version(version)

    sub = ""
    if version[3] != "final":
        mapping = {"alpha": "a", "beta": "b", "rc": "rc"}
        sub = mapping[version[3]] + str(version[4])

    return str(main + sub)


class ReleaseManager(models.Manager):
    def published(self, at=None):
        """
        List of published releases at a given date (today by default).

        A published release has a suitable publication date and is active.

        The resulting queryset is sorted by decreasing version number.

        This is expected to return the latest micro-release in each series.
        """
        if at is None:
            at = datetime.date.today()
        # .filter(date__lte=at) excludes releases where date IS NULL because
        # a version without a date is considered unreleased.
        # .exclude(eol_date__lte=at) includes releases where eol_date IS NULL
        # because a version without an end of life date is still supported.
        return (
            self.filter(major__gte=1, date__lte=at, is_active=True)
            .exclude(eol_date__lte=at)
            .order_by("-major", "-minor", "-micro", "-status")
        )

    def supported(self, at=None):
        """
        List of supported final releases.
        """
        return self.published(at).filter(status="f")

    def unsupported(self, at=None):
        """
        List of unsupported final releases at a given date (today by default).

        This returns a list, not a queryset, because it requires logic that is
        hard to express in SQL.

        Pre-1.0 releases are ignored.
        """
        if at is None:
            at = datetime.date.today()
        excluded_major_minor = {
            (release.major, release.minor) for release in self.supported(at)
        }
        unsupported = []
        for release in self.filter(major__gte=1, eol_date__lte=at, status="f").order_by(
            "-major", "-minor", "-micro"
        ):
            if (release.major, release.minor) not in excluded_major_minor:
                excluded_major_minor.add((release.major, release.minor))
                unsupported.append(release)
        return unsupported

    def current(self, at=None):
        """
        Current release.
        """
        return self.supported(at).first()

    def previous(self, at=None):
        """
        Previous release.
        """
        return self.supported(at)[1:].first()

    def lts(self, at=None):
        """
        List of supported LTS releases.
        """
        return self.supported(at).filter(is_lts=True)

    def current_lts(self, at=None):
        """
        Current LTS release.
        """
        return self.lts(at).first()

    def previous_lts(self, at=None):
        """
        Previous LTS release or None if there's only one LTS release currently.
        """
        return self.lts(at)[1:].first()

    def preview(self, at=None):
        """
        Preview release or None if there isn't a preview release currently.
        """
        return self.published(at).exclude(status="f").first()

    def current_version(self):
        current_version = cache.get(Release.DEFAULT_CACHE_KEY, None)
        if current_version is None:
            current_release = self.current()
            if current_release is None:
                current_version = ""
            else:
                current_version = current_release.version
            cache.set(
                Release.DEFAULT_CACHE_KEY,
                current_version,
                settings.CACHE_MIDDLEWARE_SECONDS,
            )
        return current_version


def get_storage():
    """
    Return a FileSystemStorage that allows file name overwrites.

    The actual file name of release artifacts (tarball, wheel, ...) should not
    be modified on upload (i.e. no prefix should be added).
    """
    return FileSystemStorage(allow_overwrite=True)


def upload_to_artifact(release, filename):
    major, minor = release.version_tuple[:2]
    return f"releases/{major}.{minor}/{filename}"


def upload_to_checksum(release, filename):
    version = get_version(release.version_tuple)
    return f"pgp/Django-{version}.checksum.txt"


class Release(models.Model):
    DEFAULT_CACHE_KEY = "%s_django_version" % settings.CACHE_MIDDLEWARE_KEY_PREFIX
    STATUS_CHOICES = (
        ("a", "alpha"),
        ("b", "beta"),
        ("c", "release candidate"),
        ("f", "final"),
    )
    STATUS_REVERSE = {
        "alpha": "a",
        "beta": "b",
        "rc": "c",
        "final": "f",
    }

    version = models.CharField(max_length=16, primary_key=True)
    is_active = models.BooleanField(
        help_text=(
            "Set this release as active. A release is considered active only "
            "if its date is today or in the past and this flag is enabled. "
            "Enable this flag when the release is available on PyPI."
        ),
        default=False,
    )
    date = models.DateField(
        "Release date",
        null=True,
        blank=True,
        default=datetime.date.today,
        help_text="Leave blank if the release date isn't know yet, typically "
        "if you're creating the final release just after the alpha "
        "because you want to build docs for the upcoming version.",
    )
    eol_date = models.DateField(
        "End of life date",
        null=True,
        blank=True,
        help_text="Leave blank if the end of life date isn't known yet, "
        "typically because it depends on the release date of a "
        "later version.",
    )

    major = models.PositiveSmallIntegerField(editable=False)
    minor = models.PositiveSmallIntegerField(editable=False)
    micro = models.PositiveSmallIntegerField(editable=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, editable=False)
    iteration = models.PositiveSmallIntegerField(editable=False)
    is_lts = models.BooleanField(
        "Long Term Support",
        help_text=(
            'Is this a release for an <abbr title="Long Term Support">LTS</abbr> Django '
            "version (e.g. 5.2a1, 5.2, 5.2.4)?"
        ),
        default=False,
    )
    # Artifacts.
    tarball = models.FileField(
        "Tarball artifact as a .tar.gz file",
        storage=get_storage,
        upload_to=upload_to_artifact,
        blank=True,
    )
    wheel = models.FileField(
        "Wheel artifact as a .whl file",
        storage=get_storage,
        upload_to=upload_to_artifact,
        blank=True,
    )
    checksum = models.FileField(
        "Signed checksum as a .asc file",
        storage=get_storage,
        upload_to=upload_to_checksum,
        blank=True,
    )

    objects = ReleaseManager()

    def save(self, *args, **kwargs):
        self.major, self.minor, self.micro, status, self.iteration = self.version_tuple
        self.status = self.STATUS_REVERSE[status]
        cache.delete(self.DEFAULT_CACHE_KEY)
        super().save(*args, **kwargs)
        if self.is_active:
            self.set_previous_release_as_eol()

    def __str__(self):
        return self.version

    @property
    def is_published(self):
        return (
            self.is_active
            and self.date is not None
            and self.date <= datetime.date.today()
        )

    @cached_property
    def version_tuple(self):
        """Return a tuple in the format of django.VERSION."""
        version = self.version.replace("-", "").replace("_", "")
        version = list(get_loose_version_tuple(version))
        if len(version) == 2:
            version.append(0)
        if not isinstance(version[2], int):
            version.insert(2, 0)
        if len(version) == 3:
            version.append("final")
        if version[3] not in ("alpha", "beta", "rc", "final"):
            version[3] = {"a": "alpha", "b": "beta", "c": "rc"}[version[3]]
        if len(version) == 4:
            version.append(0)
        return tuple(version)

    def clean(self):
        if self.is_published and not self.tarball:
            raise ValidationError(
                {"tarball": "This field is required when the release is active."}
            )

        if (self.tarball or self.wheel) and not self.checksum:
            raise ValidationError(
                {
                    "checksum": (
                        "This field is required when an artifact has been uploaded."
                    )
                }
            )

        if self.tarball:
            try:
                self.validate_artifact_name(self.tarball.name, suffix=".tar.gz")
            except ValidationError as e:
                raise ValidationError({"tarball": e})

        if self.wheel:
            try:
                self.validate_artifact_name(self.wheel.name, suffix="-py3-none-any.whl")
            except ValidationError as e:
                raise ValidationError({"wheel": e})

    def validate_artifact_name(self, name, suffix):
        name = Path(name).name  # strip any folder name if present
        version = get_version(self.version_tuple)
        regex = f"^[Dd]jango-{re.escape(version)}{re.escape(suffix)}$"
        message = f"Filename {name} does not match pattern {regex}."
        return RegexValidator(regex, message=message, code="invalid_name")(name)

    def set_previous_release_as_eol(self):
        """Handles setting EOL date for the previous release in the series."""
        previous_release_kwargs = {
            "major": self.major,
            "minor": self.minor,
            "micro": self.micro,
            "status": self.status,
            "eol_date__isnull": True,
        }
        if self.iteration > 1:
            previous_release_kwargs["iteration"] = self.iteration - 1
        elif self.status == "a":
            return
        elif self.status == "b":
            previous_release_kwargs["status"] = "a"
        elif self.status == "c":
            previous_release_kwargs["status"] = "b"
        elif self.status == "f" and self.micro == 0:
            previous_release_kwargs["status"] = "c"
        elif self.status == "f" and self.micro > 0:
            previous_release_kwargs["micro"] = self.micro - 1

        self.__class__.objects.filter(**previous_release_kwargs).update(
            eol_date=self.date
        )
