from django.conf.urls import patterns, url, include

from docs.sitemaps import DocsSitemap
from docs.urls import urlpatterns as docs_urlpatterns

sitemaps = {'docs': DocsSitemap}

urlpatterns = patterns('',
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
) + docs_urlpatterns
