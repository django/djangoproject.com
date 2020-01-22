from distutils.version import LooseVersion

from django import template
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django_hosts.resolvers import reverse

from ..models import Release

register = template.Library()


@register.simple_tag()
def release_notes(version, show_version=False):
    version_x_dot_y = '.'.join(str(x) for x in LooseVersion(version).version[:2])
    is_pre_release = any(c in version for c in ('a', 'b', 'c'))
    # links for prereleases don't have their own release notes
    display_version = version_x_dot_y if is_pre_release else version
    if show_version:
        anchor_text = _('%(version)s release notes') % {'version': display_version}
    else:
        anchor_text = _('Online documentation')
    release_notes_path = 'releases/%s' % display_version
    return format_html(
        '<a href="{url}">{anchor_text}</a>',
        url=reverse(
            'document-detail',
            host='docs',
            kwargs={'lang': 'en', 'version': version_x_dot_y, 'url': release_notes_path},
        ),
        anchor_text=anchor_text,
    )


@register.simple_tag()
def get_latest_micro_release(version):
    """
    Given an X.Y version number, return the latest X.Y.Z version.
    """
    major, minor = version.split('.')
    release = Release.objects.filter(major=major, minor=minor, status='f').order_by('-micro').first()
    if release:
        return release.version
