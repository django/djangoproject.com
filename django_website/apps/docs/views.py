import os
import re
import urlparse
from django.conf import settings
from django.core.cache import cache
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django_website.apps.docs.models import DocumentRelease
from django_website.apps.docs import builder
import pysvn

def doc_index(request, version=None):
    client, version, docroot = _get_svnroot(version, "docs/")
    doclist = client.ls(docroot, recurse=False)
    
    # Convert list of URLs to list of document slugs.
    doclist = [os.path.splitext(os.path.basename(doc.name))[0] for doc in doclist]
    doclist.sort()
    
    return render_to_response(
        ["docs/%s_index.html" % version, "docs/index.html"],
        {"version" : version, "document_list" : doclist, "all_versions" : DocumentRelease.objects.all()},
        RequestContext(request, {})
    )

def doc_detail(request, slug, version=None):
    client, version, docroot = _get_svnroot(version, "docs/")

    docpath = urlparse.urljoin(docroot, slug+".txt")
    try:
        name, info = client.info2(docpath)[0]
    except pysvn.ClientError:
        raise Http404("Invalid doc: %r (version %r)" % (slug, version))
        
    cache_key = "djangowebsite:docs:%s:%s:%s" % (version, slug, info.rev.number)
    parts = cache.get(cache_key)
    if parts is None:
        parts = builder.build_document(client.cat(docpath))
        cache.set(cache_key, parts, 60*60)
        
    return render_to_response(
        ["docs/%s_detail.html" % version, "docs/detail.html"],
        {"doc" : parts, "version" : version, "all_versions" : DocumentRelease.objects.all(), "slug" : slug},
        RequestContext(request, {})
    )

docstring_re = re.compile(r"([\"']{3})(.*?)(\1)", re.DOTALL|re.MULTILINE)
def model_index(request, version=None):
    client, version, testroot = _get_svnroot(version, "tests/modeltests/")
    
    cache_key = "djangowebsite:docs:modelindex:%s" % version
    model_docs = cache.get(cache_key, [])
    if not model_docs:
        for testdir in client.ls(testroot):
            try:
                content = client.cat(os.path.join(testdir.name, "models.py"))
            except pysvn.ClientError:
                continue
            title, blurb = docstring_re.match(content).group(2).strip().split('\n', 1)
            try:
                number, title = title.split(". ", 1)
                number = int(number)
            except ValueError:
                number = None
            model_docs.append({"title" : title, "link" : os.path.basename(testdir.name), "number" : number})
            
        model_docs.sort(lambda a,b: cmp(a["number"], b["number"]))
        
        cache.set(cache_key, model_docs, 60*60)
        
    return render_to_response(
        ["docs/%s_model_index.html" % version, "docs/model_index.html"],
        {"example_list" : model_docs, "version" : version, "all_versions" : DocumentRelease.objects.all()},
        RequestContext(request, {})
    )
    
def model_detail(request, slug, version=None):
    client, version, modelfile = _get_svnroot(version, "tests/modeltests/%s/models.py" % slug)
    name, info = client.info2(modelfile)[0]
    
    cache_key = "djangowebsite:docs:model:%s:%s:%s" % (version, slug, info.rev.number)
    parts = cache.get(cache_key)
    if parts is None:
        parts = builder.build_model_document(client.cat(modelfile))
        cache.set(cache_key, parts, 60*60)
        
    return render_to_response(
        ["docs/%s_model_detail.html" % version, "docs/model_detail.html"],
        {"doc" : parts, "version" : version, "all_versions" : DocumentRelease.objects.all(), "slug" : slug},
    )
    
def _get_svnroot(version, subpath):
    client = pysvn.Client()

    if version is None:
        version = "trunk"
        subpath = os.path.join("trunk/", subpath)
    else:
        rel = get_object_or_404(DocumentRelease, version=version)
        subpath = os.path.join(rel.repository_path, subpath)
    docroot = urlparse.urljoin(settings.DJANGO_SVN_ROOT, subpath)

    try:
        client.info2(docroot, recurse=False)
    except pysvn.ClientError:
        raise Http404("Bad SVN path: %s" % docroot)
        
    return client, version, docroot