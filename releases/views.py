from __future__ import absolute_import, unicode_literals

from django.http import HttpResponsePermanentRedirect, Http404
from django.shortcuts import get_object_or_404, render

from .models import Release


def index(request):
    # Build a dictionary of x => latest 1.x.y release
    releases = {}
    for release in Release.objects.final().order_by('minor', 'micro'):
        releases[release.minor] = release
    releases = [releases[minor] for minor in sorted(releases)]
    current = releases.pop()
    previous = releases.pop()
    context = {
        'current_version': current.version,
        'previous_version': previous.version,
        'earlier_versions': [release.version for release in reversed(releases)],
    }
    return render(request, 'releases/download.html', context)


def redirect(request, version, kind):
    release = get_object_or_404(Release, version=version)
    try:
        redirect_url = release.get_redirect_url(kind)
    except ValueError:
        raise Http404
    return HttpResponsePermanentRedirect(redirect_url)
