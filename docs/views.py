from __future__ import absolute_import

import datetime
import json

import django.views.static
from django.core import urlresolvers
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import translation

import haystack.views

from .forms import DocSearchForm
from .models import DocumentRelease
from .utils import get_doc_root_or_404, get_doc_path_or_404


def index(request):
    return redirect(DocumentRelease.objects.current())


def language(request, lang):
    return redirect(DocumentRelease.objects.current(lang))


def stable(request, lang, version, url):
    path = request.get_full_path()
    current_version = DocumentRelease.objects.current_version()
    return redirect(path.replace(version, current_version, 1))


def document(request, lang, version, url):
    # If either of these can't be encoded as ascii then later on down the line an
    # exception will be emitted by unipath, proactively check for bad data (mostly
    # from the Googlebot) so we can give a nice 404 error.
    try:
        version.encode("ascii")
        url.encode("ascii")
    except UnicodeEncodeError:
        raise Http404

    if lang != 'en':
        translation.activate(lang)

    docroot = get_doc_root_or_404(lang, version)
    doc_path = get_doc_path_or_404(docroot, url)

    if version == 'dev':
        rtd_version = 'latest'
    elif version >= '1.5':
        rtd_version = version + '.x'
    else:
        rtd_version = version + '.X'

    template_names = [
        'docs/%s.html' % docroot.rel_path_to(doc_path).replace(doc_path.ext, ''),
        'docs/doc.html',
    ]
    context = {
        'doc': json.load(open(doc_path, 'rb')),
        'env': json.load(open(docroot.child('globalcontext.json'), 'rb')),
        'lang': lang,
        'version': version,
        'version_is_dev': version == 'dev',
        # TODO: would be nice not to hardcode this.
        'version_is_unsupported': version < '1.4',
        'rtd_version': rtd_version,
        'docurl': url,
        'update_date': datetime.datetime.fromtimestamp(docroot.child('last_build').mtime()),
        'redirect_from': request.GET.get('from', None),
    }
    return render(request, template_names, context)


class SphinxStatic(object):
    """
    Serve Sphinx static assets from a subdir of the build location.
    """
    def __init__(self, subpath):
        self.subpath = subpath

    def __call__(self, request, lang, version, path):
        return django.views.static.serve(
            request,
            document_root=get_doc_root_or_404(lang, version).child(self.subpath),
            path=path,
        )


def objects_inventory(request, lang, version):
    response = django.views.static.serve(
        request,
        document_root=get_doc_root_or_404(lang, version),
        path="objects.inv",
    )
    response['Content-Type'] = "text/plain"
    return response


def redirect_index(request, *args, **kwargs):
    assert request.path.endswith('index/')
    return redirect(request.path[:-6])


class DocSearchView(haystack.views.SearchView):
    def __init__(self, **kwargs):
        kwargs.update({
            'template': 'docs/search.html',
            'form_class': DocSearchForm,
            'load_all': False,
        })
        super(DocSearchView, self).__init__(**kwargs)

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}
        pk = self.request.GET.get('release')
        if pk:
            form_kwargs['default_release'] = get_object_or_404(DocumentRelease, pk=pk)
        else:
            form_kwargs['default_release'] = DocumentRelease.objects.current()
        return super(DocSearchView, self).build_form(form_kwargs)

    def extra_context(self):
        # Constuct a context that matches the rest of the doc page views.
        current_release = self.form.default_release
        if current_release.lang != 'en':
            translation.activate(current_release.lang)
        return {
            'lang': current_release.lang,
            'version': current_release.version,
            'release': current_release,
        }
