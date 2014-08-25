from .models import Release


def django_version(request):
    return {'DJANGO_VERSION': Release.objects.current_version()}
