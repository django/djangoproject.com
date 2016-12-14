import datetime
from distutils.version import LooseVersion

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.functional import cached_property
from django.utils.version import get_complete_version, get_main_version


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

    sub = ''
    if version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'rc'}
        sub = mapping[version[3]] + str(version[4])

    return str(main + sub)


class ReleaseManager(models.Manager):

    def active(self, at=None):
        """
        List of active releases at a given date (today by default).

        The resulting queryset is sorted by decreasing version number.

        This is expected to return the latest micro-release in each series.
        """
        if at is None:
            at = datetime.date.today()
        # .filter(date__lte=at) excludes releases where date IS NULL because
        # a version without a date is considered unreleased.
        # .exclude(eol_date__lte=at) includes releases where eol_date IS NULL
        # because a version without an end of life date is still supported.
        return (self.filter(major__gte=1, date__lte=at)
                    .exclude(eol_date__lte=at)
                    .order_by('-major', '-minor', '-micro', '-status'))

    def supported(self, at=None):
        """
        List of supported final releases.
        """
        return self.active(at).filter(status='f')

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
            (release.major, release.minor)
            for release in self.supported(at)
        }
        unsupported = []
        for release in (self.filter(major__gte=1, eol_date__lte=at, status='f')
                            .order_by('-major', '-minor', '-micro')):
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
        return self.active(at).exclude(status='f').first()

    def current_version(self):
        current_version = cache.get(Release.DEFAULT_CACHE_KEY, None)
        if current_version is None:
            current_release = self.current()
            if current_release is None:
                current_version = ''
            else:
                current_version = current_release.version
            cache.set(
                Release.DEFAULT_CACHE_KEY,
                current_version,
                settings.CACHE_MIDDLEWARE_SECONDS,
            )
        return current_version


class Release(models.Model):

    DEFAULT_CACHE_KEY = "%s_django_version" % settings.CACHE_MIDDLEWARE_KEY_PREFIX
    STATUS_CHOICES = (
        ('a', 'alpha'),
        ('b', 'beta'),
        ('c', 'release candidate'),
        ('f', 'final'),
    )
    STATUS_REVERSE = {
        'alpha': 'a',
        'beta': 'b',
        'rc': 'c',
        'final': 'f',
    }

    version = models.CharField(max_length=16, primary_key=True)
    date = models.DateField(
        "Release date",
        null=True, blank=True,
        default=datetime.date.today,
        help_text="Leave blank if the release date isn't know yet, typically "
                  "if you're creating the final release just after the alpha "
                  "because you want to build docs for the upcoming version.")
    eol_date = models.DateField(
        "End of life date",
        null=True, blank=True,
        help_text="Leave blank if the end of life date isn't known yet, "
                  "typically because it depends on the release date of a "
                  "later version.")

    major = models.PositiveSmallIntegerField(editable=False)
    minor = models.PositiveSmallIntegerField(editable=False)
    micro = models.PositiveSmallIntegerField(editable=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, editable=False)
    iteration = models.PositiveSmallIntegerField(editable=False)

    is_lts = models.BooleanField("Long term support release", default=False)

    objects = ReleaseManager()

    def save(self, *args, **kwargs):
        self.major, self.minor, self.micro, status, self.iteration = self.version_tuple
        self.status = self.STATUS_REVERSE[status]
        cache.delete(self.DEFAULT_CACHE_KEY)
        super().save(*args, **kwargs)
        # Each micro release EOLs the previous one in the same series.
        if self.status == 'f' and self.micro > 0:
            (type(self).objects
                       .filter(major=self.major, minor=self.minor,
                               micro=self.micro - 1, status='f')
                       .update(eol_date=self.date))

    def __str__(self):
        return self.version

    @cached_property
    def version_tuple(self):
        """Return a tuple in the format of django.VERSION."""
        version = self.version.replace('-', '').replace('_', '')
        version = LooseVersion(version).version
        if len(version) == 2:
            version.append(0)
        if not isinstance(version[2], int):
            version.insert(2, 0)
        if len(version) == 3:
            version.append('final')
        if version[3] not in ('alpha', 'beta', 'rc', 'final'):
            version[3] = {'a': 'alpha', 'b': 'beta', 'c': 'rc'}[version[3]]
        if len(version) == 4:
            version.append(0)
        return tuple(version)

    def get_redirect_url(self, kind):
        directory = '%d.%d' % self.version_tuple[:2]
        # Django gained PEP 386 numbering in 1.4b1.
        if self.version_tuple >= (1, 4, 0, 'beta', 0):
            actual_version = get_version(self.version_tuple)
        else:
            actual_version = self.version

        if kind == 'tarball':
            pattern = '%(media)sreleases/%(directory)s/Django-%(version)s.tar.gz'

        elif kind == 'checksum':
            if self.version_tuple[:3] >= (1, 0, 4):
                pattern = '%(media)spgp/Django-%(version)s.checksum.txt'
            else:
                raise ValueError('No checksum for this version')
        else:
            raise ValueError('Unknown file')

        return pattern % {
            'media': settings.MEDIA_URL,
            'directory': directory,
            'version': actual_version,
            'major': self.version_tuple[0],
            'minor': self.version_tuple[1],
        }


def create_releases_up_to_1_5():
    if Release.objects.exists():
        raise Exception("Releases already exist, aborting.")
    versions = [                        # extracted from the redirects table
        '0.90',
        '0.91', '0.91.1', '0.91.2', '0.91.3',
        '0.95', '0.95.1', '0.95.2', '0.95.3', '0.95.4',
        '0.96', '0.96.1', '0.96.2', '0.96.3', '0.96.4', '0.96.5',
        '1.0-alpha', '1.0-alpha-2', '1.0-beta-1', '1.0-beta-2', '1.0-rc_1', '1.0', '1.0.1-beta-1', '1.0.1', '1.0.2', '1.0.3', '1.0.4',
        '1.1-rc-1', '1.1.1', '1.1.2', '1.1.3', '1.1.4', '1.1',
        '1.2-alpha-1', '1.2-beta-1', '1.2-rc-1', '1.2', '1.2.1', '1.2.2', '1.2.3', '1.2.4', '1.2.5', '1.2.6', '1.2.7',
        '1.3-alpha-1', '1.3-beta-1', '1.3-rc-1', '1.3', '1.3.1', '1.3.2', '1.3.3', '1.3.4', '1.3.5', '1.3.6', '1.3.7',
        '1.4-alpha-1', '1.4-beta-1', '1.4-rc-1', '1.4-rc-2', '1.4', '1.4.1', '1.4.2', '1.4.3', '1.4.4', '1.4.5',
        '1.5a1', '1.5b1', '1.5b2', '1.5c1', '1.5c2', '1.5',
    ]
    for version in versions:
        Release.objects.create(version=version)
