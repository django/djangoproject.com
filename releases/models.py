import datetime
import re
from functools import total_ordering
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.validators import RegexValidator
from django.db import models
from django.utils.functional import cached_property

from .utils import (
    get_django_version_tuple,
    get_feature_version,
    get_main_version,
    get_version_tuple,
    is_calendar_version,
)


# Adapted from django.utils.version.get_version(), dropping the ".devN" suffix
# it appends to an alpha 0, as that inspects the local git repository, which is
# this website rather than Django, and building the main version with the local
# get_main_version(), aware of calendar versions (DEP 20).
#
# Django 6.2: core's own get_version() serves both schemes from then on, but
# keep this one unless we are content for a release row to reach the git
# subprocess. Only an alpha 0 does, and no such release is ever published.
def get_version(version):
    """Return a PEP 440-compliant version number from a version tuple."""
    # The two parts of the version number:
    # main = A.B[.C] or YYYY[.N]
    # sub = {a|b|rc}N - for alpha, beta and rc releases
    main = get_main_version(version)

    # Read the status from the end, as calendar versions have one component
    # less than A.B.C ones, and so shift every index before it.
    *_, status, iteration = version
    sub = ""
    if status != "final":
        mapping = {"alpha": "a", "beta": "b", "rc": "rc"}
        sub = mapping[status] + str(iteration)

    return main + sub


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
        # The feature version names a series under either scheme. Grouping by
        # (major, minor) would split a calendar series into one entry per patch
        # release, as minor is the patch number there. See DEP 20.
        seen_series = {release.feature_version for release in self.supported(at)}
        unsupported = []
        for release in self.filter(major__gte=1, eol_date__lte=at, status="f").order_by(
            "-major", "-minor", "-micro"
        ):
            if release.feature_version not in seen_series:
                seen_series.add(release.feature_version)
                unsupported.append(release)
        return unsupported

    def in_feature_series(self, release):
        """
        Final releases in the same feature series as `release`, newest first.

        A calendar version's series is its year alone, as its minor component
        is the patch number, while an A.B one's is major and minor together.
        """
        series = {"major": release.major}
        if not release.is_calendar_version:
            series["minor"] = release.minor
        return self.filter(status="f", **series).order_by("-minor", "-micro")

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


# Artifact file names are Django-<version><suffix>, where the suffix is
# .tar.gz for tarballs and -py3-none-any.whl for wheels. Release.clean()
# validates the whole name; this only extracts the version, so that an
# artifact is never filed under a release it doesn't belong to.
artifact_name_re = re.compile(
    r"^[^-]+-(?P<version>[^-]+?)(?:\.tar\.[a-z]+|-py3-none(?:-any)?\.whl)$",
    re.IGNORECASE,
)


def get_storage():
    """
    Return a FileSystemStorage that allows file name overwrites.

    The actual file name of release artifacts (tarball, wheel, ...) should not
    be modified on upload (i.e. no prefix should be added).
    """
    return FileSystemStorage(allow_overwrite=True)


def upload_to_artifact(release, filename):
    name = Path(filename).name
    version = get_version(release.version_tuple)
    match = artifact_name_re.match(name)
    if match is None or match["version"] != version:
        raise ValidationError(
            f"Filename {name} does not belong to the {version} release."
        )
    return f"releases/{release.feature_version}/{filename}"


def upload_to_checksum(release, filename):
    version = get_version(release.version_tuple)
    return f"pgp/Django-{version}.checksum.txt"


@total_ordering
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
        help_text="Leave blank if the release date isn't known yet, typically "
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
            'Is this a release for an <abbr title="Long Term Support">LTS</abbr> '
            "Django version (e.g. 5.2a1, 5.2, 5.2.4)? Always set for calendar "
            "versions, which are all supported for three years."
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
        # DEP 20 gives every calendar version three years of support, retiring
        # the LTS label as a distinguishing one. Set here rather than as a
        # field default, which cannot know the version.
        self.is_lts = self.is_lts or is_calendar_version(self.major)
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
        """Return the five components backing the major/minor/micro fields."""
        return get_version_tuple(self.version)

    @cached_property
    def django_version_tuple(self):
        """Return the version tuple as django.VERSION spells it.

        Django 6.2: return a django.utils.version.VersionTuple instead, and
        drop get_django_version_tuple().
        """
        return get_django_version_tuple(self.version)

    @cached_property
    def version_verbose(self):
        return (
            f"{self.feature_version} {self.get_status_display()} {self.iteration}"
            if self.is_pre_release
            else self.version
        )

    @cached_property
    def feature_version(self):
        return get_feature_version(self.version)

    @cached_property
    def feature_release(self):
        return Release.objects.get(version=self.feature_version)

    @cached_property
    def series(self):
        return f"{self.major}.x"

    @cached_property
    def stable_branch(self):
        return f"stable/{self.feature_version}.x"

    @cached_property
    def commit_prefix(self):
        return f"[{self.feature_version}.x]"

    @cached_property
    def is_pre_release(self):
        """Return True if this is an alpha, beta, or rc release."""
        return self.status != "f"

    @cached_property
    def is_calendar_version(self):
        """Return True if this release is calendar versioned (YYYY[.N])."""
        # The module level function, not this property.
        return is_calendar_version(self.major)

    @cached_property
    def show_lts_label(self):
        """Return True if this release should be labelled LTS to readers.

        The flag stays set for calendar versions, which are all supported for
        three years, but the label is not shown for them: it only ever meant
        "supported for longer than the others". See DEP 20.
        """
        return self.is_lts and not self.is_calendar_version

    @cached_property
    def is_dot_zero(self):
        """Return True if this is a final feature release (X.Y or YYYY)."""
        return (
            self.status == "f"
            and self.micro == 0
            and (not self.is_calendar_version or self.minor == 0)
        )

    def __lt__(self, other):
        return self.version_tuple < other.version_tuple

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
        elif self.status == "f" and self.is_calendar_version and self.minor > 0:
            previous_release_kwargs["minor"] = self.minor - 1
        elif self.status == "f" and self.micro == 0:
            previous_release_kwargs["status"] = "c"
        elif self.status == "f" and self.micro > 0:
            previous_release_kwargs["micro"] = self.micro - 1

        self.__class__.objects.filter(**previous_release_kwargs).update(
            eol_date=self.date
        )
