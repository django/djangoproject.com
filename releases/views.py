from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render

from .models import Release
from .utils import FIRST_CALENDAR_VERSION_YEAR


def index(request):
    # Look for regular releases.
    current = Release.objects.current()
    previous = Release.objects.previous()

    # Look for an LTS release, if there is one.
    lts = Release.objects.current_lts()
    if lts in (current, previous):
        # There might be a previous LTS release that's still supported.
        lts = Release.objects.previous_lts()

    # Look for a preview release, if there is one.
    preview = Release.objects.preview()

    # Get the list of earlier releases.
    unsupported = Release.objects.unsupported()

    context = {
        "current": current,
        "previous": previous,
        "lts": lts,
        "unsupported": unsupported,
        "preview": preview,
    }
    return render(request, "releases/download.html", context)


def roadmap(request, series):
    major, _, minor = series.partition(".")
    major = int(major)
    minor = int(minor or 0)
    if major < 2:
        raise Http404

    releases = Release.objects.filter(major=major, minor=minor, micro=0)
    context = {
        "series": series,
        # Do not rely on the final release existing yet, roadmap pages are
        # published before any release in the series is created.
        "is_calendar_version": major >= FIRST_CALENDAR_VERSION_YEAR,
        "releases": {r.status: r for r in releases},
    }
    return render(request, "releases/roadmap.html", context)


def redirect(request, version, kind):
    release = get_object_or_404(Release, version=version)

    if not (artifact := getattr(release, kind, None)):
        raise Http404

    return HttpResponsePermanentRedirect(artifact.url)
