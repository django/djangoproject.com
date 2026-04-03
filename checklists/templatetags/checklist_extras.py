from datetime import timedelta

from django import template

register = template.Library()


@register.filter
def next_version(release):
    return f"{release.major}.{release.minor}.{release.micro + 1}"


@register.filter
def next_feature_version(release):
    if release.minor < 2:
        result = f"{release.major}.{release.minor + 1}"
    else:
        result = f"{release.major + 1}.0"
    return result


@register.filter
def format_version_tuple(version_tuple):
    version_tuple = [str(v) for v in version_tuple]
    version_tuple[3] = f'"{version_tuple[3]}"'
    version_tuple = ", ".join(version_tuple)
    return f"({version_tuple})"


@register.filter
def next_version_tuple(release):
    return release.major, release.minor, release.micro + 1, "alpha", 0


@register.filter
def next_release_date(value):
    return value + timedelta(days=30)


@register.filter
def enumerate_items(items, item_formatter=None):
    if item_formatter is not None:
        items = [item_formatter(item) for item in items]
    if not items:
        return ""
    *rest, last = items
    if not rest:
        return last

    last_joiner = ", and " if len(rest) > 1 else " and "  # Oxford comma
    return last_joiner.join((", ".join(rest), last))


@register.filter
def enumerate_cves(cves, field="cve_year_number"):
    return enumerate_items([getattr(cve, field) for cve in cves])


@register.filter
def format_release_for_cve(release):
    return f"{release.feature_version} before {release.version}"


@register.filter
def format_releases_for_cves(releases):
    return enumerate_items(
        [r for r in releases if not r.is_pre_release],
        item_formatter=format_release_for_cve,
    )


@register.filter
def format_version_for_blogpost(version):
    return (
        f"`Django {version} "
        f"<https://docs.djangoproject.com/en/dev/releases/{version}/>`_"
    )


@register.filter
def format_versions_for_blogpost(versions):
    return enumerate_items(versions, item_formatter=format_version_for_blogpost)


@register.filter
def rst_backticks(text):
    return text.replace("`", "``")


@register.filter
def rst_underline_for_headline(headline, headline_char="="):
    headline_underline = headline_char * len(headline)
    return f"{headline}\n{headline_underline}"


@register.filter
def stub_release_notes_title(version):
    title = f"Django {version} release notes"
    title_underline = "=" * len(title)
    return f"{title_underline}\n{title}\n{title_underline}"
