import cPickle as pickle
import datetime
import django.views.static
from django.conf import settings
from django.core import urlresolvers
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
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
    if lang != 'en' or version != 'dev' or url == "search/": raise Http404()

    docroot = Path(settings.DOCS_PICKLE_ROOT)

    # First look for <bits>/index.fpickle, then for <bits>.fpickle
    bits = url.strip('/').split('/')
    doc = docroot.child(*(bits+['index.fpickle']))
    if not doc.exists():
        doc = docroot.child(*bits[:-1] + ["%s.fpickle" % bits[-1]])
        if not doc.exists():
            raise Http404("'%s' does not exist" % doc)
    
    # Build up a list of templates to search for so that if the page is
    # "ref/models", the list will be ["docs/ref/models.html", "docs/ref.html"]
    bits[-1] = bits[-1].replace('.fpickle', '')
    templates = ["docs/%s.html" % "/".join(bits[:-i+1]) for i in range(len(bits))]    
    return render_to_response(templates + ['docs/doc.html'], {
        'doc': pickle.load(open(doc)),
        'env': pickle.load(open(docroot.child('globalcontext.pickle'))),
        'update_date': datetime.datetime.fromtimestamp(docroot.child('last_build').mtime()),
        'home': urlresolvers.reverse(document, kwargs={'lang':lang, 'version':version, 'url':''}),
    })

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