from django.views import static

from .models import DocumentRelease
from .utils import get_doc_root_or_404


def sphinx_static(request, lang, version, path, subpath):
    """
    Serve Sphinx static assets from a subdir of the build location.
    """
    document_root = get_doc_root_or_404(lang, version) / subpath
    return static.serve(request, document_root=document_root, path=path)


def objects_inventory(request, lang, version):
    response = static.serve(
        request,
        document_root=get_doc_root_or_404(lang, version),
        path="objects.inv",
    )
    response["Content-Type"] = "text/plain"
    return response


def pot_file(request, pot_name):
    version = DocumentRelease.objects.current().version
    doc_root = get_doc_root_or_404("en", version, builder="gettext")
    return static.serve(request, document_root=doc_root, path=pot_name)
