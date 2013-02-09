from django.conf.urls import patterns, url, include
from django.http import HttpResponse

from docs.sitemaps import DocsSitemap
from docs.urls import urlpatterns as docs_urlpatterns

sitemaps = {'docs': DocsSitemap}

urlpatterns = docs_urlpatterns + patterns('',
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url(r'^google79eabba6bf6fd6d3\.html$', lambda req: HttpResponse('google-site-verification: google79eabba6bf6fd6d3.html')),
)
