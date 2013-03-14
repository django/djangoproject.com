from __future__ import absolute_import, unicode_literals

from distutils.version import LooseVersion

from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from django.utils.version import get_version


class Release(models.Model):
    version = models.CharField(max_length=16, primary_key=True)
    date = models.DateField(null=True)          # nullable until we have a date for every release

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
            version.append('alpha')
        if version[3] not in ('alpha', 'beta', 'rc'):
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
        if self.version_tuple[:3] in [(1, 0, 1), (1, 0, 2), (1, 0, 3), (1, 0, 4), (1, 1, 1)]:
            number = '%d.%d.%d' % self.version_tuple[:3]
        else:
            number = '%d.%d' % self.version_tuple[:2]
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
                pattern = '%(media)sreleases/%(number)s/Django-%(version)s.tar.gz'

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
            'number': number,
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
