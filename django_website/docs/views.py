from __future__ import absolute_import

import datetime
import django.views.static
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils import simplejson
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
        'search': urlresolvers.reverse('document-search', kwargs={'lang':lang, 'version':version}),
        'redirect_from': request.GET.get('from', None),
    }))

def images(request, lang, version, path):
    return django.views.static.serve(
        request, 
        document_root = get_doc_root_or_404(lang, version).child('_images'),
        path = path,
    )
    
def source(request, lang, version, path):
    return django.views.static.serve(
        request,
        document_root = get_doc_root_or_404(lang, version).child('_sources'),
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
    return HttpResponseRedirect(request.path.rstrip('index/'))

def search(request, lang, version):
    docroot = get_doc_root_or_404(lang, version)
    
    # Remove the 'cof' GET variable from the query string so that the page
    # linked to by the Javascript fallback doesn't think its inside an iframe.
    mutable_get = request.GET.copy()
    if 'cof' in mutable_get:
        del mutable_get['cof']
    
    return render_to_response('docs/search.html', RequestContext(request, {
        'query': request.GET.get('q'),
        'query_string': mutable_get.urlencode(),
        'lang': lang,
        'version': version,
        'env': simplejson.load(open(docroot.child('globalcontext.json'), 'rb')),
        'home': urlresolvers.reverse('document-index', kwargs={'lang':lang, 'version':version}),
        'search': urlresolvers.reverse('document-search', kwargs={'lang':lang, 'version':version}),
    }))