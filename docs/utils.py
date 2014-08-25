from django.conf import settings
from django.http import Http404

from unipath import FSPath as Path


def get_doc_root(lang, version, subroot='json'):
    return Path(settings.DOCS_BUILD_ROOT).child(lang, version, "_built", subroot)


def get_doc_root_or_404(lang, version, subroot='json'):
    docroot = get_doc_root(lang, version, subroot)
    if not docroot.exists():
        raise Http404(docroot)
    return docroot


def get_doc_path(docroot, subpath):
    # First look for <bits>/index.fjson, then for <bits>.fjson
    bits = subpath.strip('/').split('/') + ['index.fjson']
    doc = docroot.child(*bits)
    if doc.exists():
        return doc

    bits = bits[:-2] + ['%s.fjson' % bits[-2]]
    doc = docroot.child(*bits)
    if doc.exists():
        return doc

    return None


def get_doc_path_or_404(docroot, subpath):
    doc = get_doc_path(docroot, subpath)
    if doc is None:
        raise Http404(doc)
    return doc
