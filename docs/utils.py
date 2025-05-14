import re
import unicodedata

from django.conf import settings
from django.http import Http404


def get_doc_root(lang, version, builder="json"):
    return settings.DOCS_BUILD_ROOT.joinpath(lang, version, "_built", builder)


def get_doc_root_or_404(lang, version, builder="json"):
    docroot = get_doc_root(lang, version, builder)
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


def get_module_path(name, full_path):
    """
    Checks if the `full_path` ends with `.name` and, if so, removes it to return
    the module path. Otherwise, it returns `None`.

    Args:
        name (str):
            The short name of the object (e.g., `"QuerySet.select_related"`).
        full_path (str):
            The full path of the object (e.g.,
            `"django.db.models.query.QuerySet.select_related"`).

    Returns:
        str or None:
            The module path if `full_path` ends with `.name`, otherwise `None`.

    Example:
        >>> get_module_path(
        ...   "QuerySet.select_related",
        ...   "django.db.models.query.QuerySet.select_related"
        ... )
        'django.db.models.query'

        >>> get_module_path("Model", "django.db.models.Model")
        'django.db.models'

        >>> get_module_path("django", "django")
        None
    """
    name_suffix = f".{name}"
    if full_path.endswith(name_suffix):
        return full_path.removesuffix(name_suffix)
    return None
