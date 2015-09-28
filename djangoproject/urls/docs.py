from django.conf.urls import include, url
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse

from docs.sitemaps import DocsSitemap
from docs.urls import urlpatterns as docs_urlpatterns

sitemaps = {'docs': DocsSitemap}


urlpatterns = docs_urlpatterns + [
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}),
    url(r'^google79eabba6bf6fd6d3\.html$', lambda req: HttpResponse('google-site-verification: google79eabba6bf6fd6d3.html')),
    # This just exists to make sure we can proof that the error pages work under both hostnames.
    url(r'', include('legacy.urls')),
]
