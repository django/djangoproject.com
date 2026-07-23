from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django_hosts.resolvers import reverse

from ..models import Release
from ..utils import get_feature_version

register = template.Library()


@register.simple_tag()
def release_notes(version, show_version=False):
    feature_version = get_feature_version(version)
    is_pre_release = any(c in version for c in ("a", "b", "c"))
    # links for prereleases don't have their own release notes
    display_version = feature_version if is_pre_release else version
    if show_version:
        anchor_text = _("%(version)s release notes") % {"version": display_version}
    else:
        anchor_text = _("Online documentation")
    release_notes_path = "releases/%s" % display_version
    return format_html(
        '<a href="{url}">{anchor_text}</a>',
        url=reverse(
            "document-detail",
            host="docs",
            kwargs={
                "lang": settings.DEFAULT_LANGUAGE_CODE,
                "version": feature_version,
                "url": release_notes_path,
            },
        ),
        anchor_text=anchor_text,
    )


@register.simple_tag()
def get_latest_release_version(version):
    """
    Given an X.Y or YYYY version number, return the latest version of that release.
    """
    major, separator, minor = version.partition(".")
    filters = {
        "major": major,
        "status": "f",
        "is_active": True,
    }
    if separator:
        filters["minor"] = minor
    ordering = "-micro" if separator else "-minor"
    release = Release.objects.filter(**filters).order_by(ordering).first()
    return release.version if release else None
