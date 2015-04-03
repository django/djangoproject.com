from django import template
from django.utils.translation import ugettext as _

from django_hosts.resolvers import reverse

register = template.Library()


@register.simple_tag()
def release_notes(version, show_version=False):
    version_x_dot_y = version[:3]
    is_pre_release = any(c in version for c in ('a', 'b', 'c'))
    # links for prereleases don't have their own release notes
    display_version = version_x_dot_y if is_pre_release else version
    if show_version:
        anchor_text = _('%(version)s release notes') % {'version': display_version}
    else:
        anchor_text = _('Online documentation')
    release_notes_path = 'releases/%s' % display_version
    return '<a href="%(url)s">%(anchor_text)s</a>' % {
        'url': reverse(
            'document-detail',
            host='docs',
            kwargs={'lang': 'en', 'version': version_x_dot_y, 'url': release_notes_path},
        ),
        'anchor_text': anchor_text,
    }
