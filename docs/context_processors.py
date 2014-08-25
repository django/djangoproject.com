from docs.models import DocumentRelease


def docs_version(request):
    return {'DOCS_VERSION': DocumentRelease.objects.current_version()}
