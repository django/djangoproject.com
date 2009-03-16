import cPickle as pickle
import datetime
import django.views.static
from django.conf import settings
from django.core import urlresolvers
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from unipath import FSPath as Path
import simplejson

def index(request):
    return HttpResponseRedirect(
        urlresolvers.reverse('document-index', kwargs={
            'lang': 'en',
            'version': 'dev',
        })
    )
    
def language(request, lang):
    return HttpResponseRedirect(
        urlresolvers.reverse('document-index', kwargs={
            'lang': lang,
            'version': 'dev',
        })
    )

def document(request, lang, version, url):
    docroot = Path(settings.DOCS_PICKLE_ROOT).child(lang, version, "_build", "json")
    if not docroot.exists():
        raise Http404()

    # First look for <bits>/index.fpickle, then for <bits>.fpickle
    bits = url.strip('/').split('/') + ['index.fjson']
    doc = docroot.child(*bits)
    if not doc.exists():
        bits = bits[:-2] + ['%s.fjson' % bits[-2]]
        doc = docroot.child(*bits)
        if not doc.exists():
            raise Http404("'%s' does not exist" % doc)

    bits[-1] = bits[-1].replace('.fjson', '')
    template_names = [
        'docs/%s.html' % '-'.join([b for b in bits if b]), 
        'docs/doc.html'
    ]
    return render_to_response(template_names, RequestContext(request, {
        'doc': simplejson.load(open(doc, 'rb')),
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
    if lang != 'en' or version != 'dev': raise Http404()
    return django.views.static.serve(
        request, 
        document_root = Path(settings.DOCS_PICKLE_ROOT).child('_images'),
        path = path,
    )
    
def source(request, lang, version, path):
    if lang != 'en' or version != 'dev': raise Http404()
    return django.views.static.serve(
        request,
        document_root = Path(settings.DOCS_PICKLE_ROOT).child('_sources'),
        path = path,
    )

def search(request, lang, version):
    if lang != 'en' or version != 'dev': raise Http404()
    
    docroot = Path(settings.DOCS_PICKLE_ROOT)
    
    # Remove the 'cof' GET variable from the query string so that the page
    # linked to by the Javascript fallback doesn't think its inside an iframe.
    mutable_get = request.GET.copy()
    if 'cof' in mutable_get:
        del mutable_get['cof']
    
    return render_to_response('docs/search.html', RequestContext(request, {
        'query': request.GET.get('q'),
        'query_string': mutable_get.urlencode(),
        'env': simplejson.load(open(docroot.child('globalcontext.json'), 'rb')),
        'home': urlresolvers.reverse('document-index', kwargs={'lang':lang, 'version':version}),
        'search': urlresolvers.reverse('document-search', kwargs={'lang':lang, 'version':version}),
    }))