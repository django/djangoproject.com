import re
import unicodedata

from django.conf import settings
from django.http import Http404


def get_doc_root(lang, version, subroot="json"):
    return settings.DOCS_BUILD_ROOT.joinpath(lang, version, "_built", subroot)


def get_doc_root_or_404(lang, version, subroot="json"):
    docroot = get_doc_root(lang, version, subroot)
    if not docroot.exists():
        raise Http404(str(docroot))
    return docroot


def get_doc_path(docroot, subpath):
    # First look for <bits>/index.fjson, then for <bits>.fjson
    try:
        bits = subpath.strip("/").split("/") + ["index.fjson"]
    except AttributeError:
        bits = []
    doc = docroot.joinpath(*bits)
    try:
        if doc.exists():
            return doc
    except NotADirectoryError:
        pass  # we get here if doc + subpath (without /index.fjson) is a file

    bits = bits[:-2] + ["%s.fjson" % bits[-2]]
    doc = docroot.joinpath(*bits)
    if doc.exists():
        return doc

    return None


def get_doc_path_or_404(docroot, subpath):
    doc = get_doc_path(docroot, subpath)
    if doc is None:
        raise Http404(doc)
    return doc


def sanitize_for_trigram(text):
    """
    Sanitize search query for PostgreSQL Trigram search.

    - Removes parts starting with '-'
    - Normalizes Unicode characters (NFKD)
    - Keeps only letters, numbers and spaces
    - Removes multiple spaces and trims
    """
    text = re.sub(r'(\s|^)-[^\s"\']+|(\s|^)-["\'][^"\']+["\']', "", text)
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    return " ".join(text.split())


def generate_code_references(body):
    """
    Django documents classes with the syntax `.. class::`.
    This results in the following HTML:
    <dl class="py class">
        <dt class="sig sig-object py" id="django.db.models.ManyToManyField">
        ...
        </dt>
    </dl>
    This is similar for attributes (`.. attribute::`), methods etc.
    """
    # Collect all <dt> HTML tag ids into a list, e.g:
    # [
    #    'django.db.models.Index',
    #    'django.db.models.Index.expressions',
    #    'django.db.models.Index.fields',
    #    ...
    # ]
    code_references = list(re.findall(r'<dt[^>]+id="([^"]+)"', body))
    # As the search term can be "expressions", "Index.expressions" etc. create a mapping
    # between potential code search terms and their HTML id.
    # {
    #   'Index': 'django.db.models.Index',
    #   'Index.expressions': 'django.db.models.Index.expressions',
    #   'Index.fields': 'django.db.models.Index.fields',
    #   ...
    # }
    code_paths = {}
    for reference in code_references:
        code_path = reference.split(".")[-2:]
        if code_path[0][0].isupper():
            name = ".".join(code_path)
            code_paths[name] = reference
        else:
            code_paths[code_path[-1]] = reference
    return code_paths
