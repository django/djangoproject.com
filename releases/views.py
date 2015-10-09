from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render

from .models import Release


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
        'current': current,
        'previous': previous,
        'lts': lts,
        'unsupported': unsupported,
        'preview': preview,
    }
    return render(request, 'releases/download.html', context)


def redirect(request, version, kind):
    release = get_object_or_404(Release, version=version)
    try:
        redirect_url = release.get_redirect_url(kind)
    except ValueError:
        raise Http404
    return HttpResponsePermanentRedirect(redirect_url)
