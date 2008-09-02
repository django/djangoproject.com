import cPickle as pickle
import datetime
import django.views.static
from django.conf import settings
from django.core import urlresolvers
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from unipath import FSPath as Path

def index(request):
    return HttpResponseRedirect(
        urlresolvers.reverse(document, kwargs={
            'lang': 'en',
            'version': 'dev',
            'url': '',
        })
    )
    
def language(request, lang):
    return HttpResponseRedirect(
        urlresolvers.reverse(document, kwargs={
            'lang': lang,
            'version': 'dev',
            'url': '',
        })
    )

def document(request, lang, version, url):
    if lang != 'en' or version != 'dev': raise Http404()

    docroot = Path(settings.DOCS_PICKLE_ROOT)

    # First look for <bits>/index.fpickle, then for <bits>.fpickle
    bits = url.strip('/').split('/') + ['index.fpickle']
    doc = docroot.child(*bits)
    if not doc.exists():
        bits = bits[:-2] + ['%s.fpickle' % bits[-2]]
        doc = docroot.child(*bits)
        if not doc.exists():
            raise Http404("'%s' does not exist" % doc)

    bits[-1] = bits[-1].replace('.fpickle', '')
    template_names = [
        'docs/%s.html' % '-'.join([b for b in bits if b]), 
        'docs/doc.html'
    ]
    return render_to_response(template_names, RequestContext(request, {
        'doc': pickle.load(open(doc, 'rb')),
        'env': pickle.load(open(docroot.child('globalcontext.pickle'), 'rb')),
        'update_date': datetime.datetime.fromtimestamp(docroot.child('last_build').mtime()),
        'home': urlresolvers.reverse(document, kwargs={'lang':lang, 'version':version, 'url':''}),
        'search': urlresolvers.reverse(search, kwargs={'lang':lang, 'version':version}),
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
        'env': pickle.load(open(docroot.child('globalcontext.pickle'), 'rb')),
        'home': urlresolvers.reverse(document, kwargs={'lang':lang, 'version':version, 'url':''}),
        'search': urlresolvers.reverse(search, kwargs={'lang':lang, 'version':version}),
    }))