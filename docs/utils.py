from django.conf import settings
from django.http import Http404


def get_doc_root(lang, version, subroot='json'):
    return settings.DOCS_BUILD_ROOT.joinpath(lang, version, "_built", subroot)


def get_doc_root_or_404(lang, version, subroot='json'):
    docroot = get_doc_root(lang, version, subroot)
    if not docroot.exists():
        raise Http404(str(docroot))
    return docroot


def get_doc_path(docroot, subpath):
    # First look for <bits>/index.fjson, then for <bits>.fjson
    bits = subpath.strip('/').split('/') + ['index.fjson']
    doc = docroot.joinpath(*bits)
    try:
        if doc.exists():
            return doc
    except NotADirectoryError:
        pass  # we get here if doc + subpath (without /index.fjson) is a file

    bits = bits[:-2] + ['%s.fjson' % bits[-2]]
    doc = docroot.joinpath(*bits)
    if doc.exists():
        return doc

    return None


def get_doc_path_or_404(docroot, subpath):
    doc = get_doc_path(docroot, subpath)
    if doc is None:
        raise Http404(doc)
    return doc
