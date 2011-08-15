from __future__ import absolute_import

import datetime
import django.views.static
from django.core import urlresolvers
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils import simplejson
import haystack.views
from .forms import DocSearchForm
from .models import DocumentRelease
from .utils import get_doc_root_or_404, get_doc_path_or_404

def index(request):
    return redirect(DocumentRelease.objects.default())
    
def language(request, lang):
    return redirect(DocumentRelease.objects.default())

def document(request, lang, version, url):
    docroot = get_doc_root_or_404(lang, version)
    doc_path = get_doc_path_or_404(docroot, url)

    template_names = [
        'docs/%s.html' % docroot.rel_path_to(doc_path).replace(doc_path.ext, ''),
        'docs/doc.html',
    ]    
    return render_to_response(template_names, RequestContext(request, {
        'doc': simplejson.load(open(doc_path, 'rb')),
        'env': simplejson.load(open(docroot.child('globalcontext.json'), 'rb')),
        'lang': lang,
        'version': version,
        'docurl': url,
        'update_date': datetime.datetime.fromtimestamp(docroot.child('last_build').mtime()),
        'home': urlresolvers.reverse('document-index', kwargs={'lang':lang, 'version':version}),
        'redirect_from': request.GET.get('from', None),
    }))

class SphinxStatic(object):
    """
    Serve Sphinx static assets from a subdir of the build location.
    """
    def __init__(self, subpath):
        self.subpath = subpath

    def __call__(self, request, lang, version, path):
        return django.views.static.serve(
            request, 
            document_root = get_doc_root_or_404(lang, version).child(self.subpath),
            path = path,
        )

def objects_inventory(request, lang, version):
    response = django.views.static.serve(
        request, 
        document_root = get_doc_root_or_404(lang, version),
        path = "objects.inv",
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
    
    def extra_context(self):
        # Constuct a context that matches the rest of the doc page views.
        default_release = DocumentRelease.objects.default()
        return {
            'lang': default_release.lang,
            'version': default_release.version,
            'release': default_release,
        }
    