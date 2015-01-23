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
    # Handle preview releases
    try:
        preview = Release.objects.preview().filter(
            minor__gt=current.minor,
        ).order_by('-minor', '-micro', '-status', '-iteration')[0]
    except IndexError:
        preview_version = None
        preview_kind = None
    else:
        preview_version = preview.version
        preview_kind = {
            'a': 'alpha',
            'b': 'beta',
            'c': 'release candidate',
        }[preview.status]

    # Look for an LTS release, if there is one.
    lts = Release.objects.current_lts()
    if lts in (current, previous):
        # There might be a previous LTS release that's still supported.
        lts = Release.objects.previous_lts()

    context = {
        'current_version': current.version,
        'previous_version': previous.version,
        'lts_version': lts.version if lts else None,
        'earlier_versions': [release.version for release in reversed(releases) if release != lts],
        'preview_version': preview_version,
        'preview_kind': preview_kind,
    }
    return render(request, 'releases/download.html', context)


def redirect(request, version, kind):
    release = get_object_or_404(Release, version=version)
    try:
        redirect_url = release.get_redirect_url(kind)
    except ValueError:
        raise Http404
    return HttpResponsePermanentRedirect(redirect_url)
