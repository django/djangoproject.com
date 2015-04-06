import datetime
from distutils.version import LooseVersion

from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.utils.functional import cached_property
from django.utils.version import get_version

# How many days after the release an LTS is the previous LTS supported?
LTS_SUPPORT_OVERLAP_DAYS = 180


class ReleaseManager(models.Manager):

    def preview(self):
        return self.filter(major=1).exclude(status='f')

    def final(self):
        return self.filter(major=1, status='f')

    def current(self):
        return self.final().order_by('-minor', '-micro')[0]

    def lts(self):
        return self.final().order_by('-minor', '-micro').filter(is_lts=True)

    def current_lts(self):
        return self.lts().first()

    def previous_lts(self):
        """Get the previous LTS if it's still supported."""
        current_lts = self.current_lts()
        # Check if the previous LTS is too old to be supported.
        if datetime.date.today() - current_lts.date < datetime.timedelta(LTS_SUPPORT_OVERLAP_DAYS):
            return self.lts().exclude(minor=current_lts.minor).first()

    def current_version(self):
        current_version = cache.get(Release.DEFAULT_CACHE_KEY, None)
        if current_version is None:
            try:
                current_version = self.current().version
            except (Release.DoesNotExist, IndexError):
                current_version = ''
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
        ('c', 'rc'),
        ('f', 'final'),
    )
    STATUS_REVERSE = dict((word, letter) for (letter, word) in STATUS_CHOICES)

    version = models.CharField(max_length=16, primary_key=True)
    date = models.DateField(default=datetime.date.today)

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
        super(Release, self).save(*args, **kwargs)

    def __unicode__(self):
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
        # Hacks to account for the history of Django.
        # Some 0.9x.y releases failed and were replaced by the next one.
        superseded_by = {
            '0.91.1': '0.91.2',
            '0.95.2': '0.95.3',
            '0.96.1': '0.96.2',
        }.get(self.version)
        # Early 1.x.y releases had a different directory tree.
        has_subdir = (1, 0, 1), (1, 0, 2), (1, 0, 3), (1, 0, 4), (1, 1, 1)
        if self.version_tuple[:3] in has_subdir:
            directory = '%d.%d.%d' % self.version_tuple[:3]
        else:
            directory = '%d.%d' % self.version_tuple[:2]
        # Django gained PEP 386 numbering in 1.4b1.
        if self.version_tuple >= (1, 4, 0, 'beta', 0):
            actual_version = get_version(self.version_tuple)
        # Early 1.0.x tarballs were named inconsistently.
        else:
            actual_version = {
                '1.0-alpha-2': '1.0-alpha_2',
                '1.0-beta-1': '1.0-beta_1',
                '1.0-beta-2': '1.0-beta_2',
                '1.0.1-beta-1': '1.0.1_beta_1',
                '1.0.1': '1.0.1-final',
                '1.0.2': '1.0.2-final',
            }.get(self.version, self.version)

        if kind == 'tarball':
            if superseded_by:
                pattern = '/download/%(superseded_by)s/tarball/'
            else:
                pattern = '%(media)sreleases/%(directory)s/Django-%(version)s.tar.gz'

        elif kind == 'checksum':
            if self.version_tuple[:3] >= (1, 0, 4):
                pattern = '%(media)spgp/Django-%(version)s.checksum.txt'
            else:
                raise ValueError('No checksum for this version')

        elif kind == 'egg':
            if self.version_tuple[:3] in [(0, 90, 0), (0, 91, 0)]:
                pattern = '%(media)sreleases/%(version)s/Django-%(version)s-py2.4.egg'
            else:
                raise ValueError('No egg for this version')

        return pattern % {
            'media': settings.MEDIA_URL,
            'directory': directory,
            'version': actual_version,
            'superseded_by': superseded_by,
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
