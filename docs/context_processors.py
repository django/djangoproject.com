from docs.models import DocumentRelease

def recent_release(request):
    return {'RECENT_RELEASE': DocumentRelease.objects.default_version()}
