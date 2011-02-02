from django.conf import settings

def recent_release(request):
    return {'RECENT_RELEASE': settings.RECENT_RELEASE}
