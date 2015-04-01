from django import template

from django_hosts.resolvers import reverse

register = template.Library()


@register.simple_tag()
def release_notes(version, text=''):
    version_x_dot_y = version[:3]
    is_pre_release = any(c in version for c in ('a', 'b', 'c'))
    # links for prereleases don't have their own release notes
    display_version = version_x_dot_y if is_pre_release else version
    release_notes_path = 'releases/%s' % display_version
    return '<a href="%s">%s</a>' % (
        reverse(
            'document-detail',
            host='docs',
            kwargs={'lang': 'en', 'version': version_x_dot_y, 'url': release_notes_path},
        ),
        text if text else ('%s release notes' % display_version),
    )
