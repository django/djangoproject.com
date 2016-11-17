from collections import MutableMapping

from django.conf.urls import include, url
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse

from docs.models import DocumentRelease
from docs.sitemaps import DocsSitemap
from docs.urls import urlpatterns as docs_urlpatterns
from docs.views import sitemap_index


class Sitemaps(MutableMapping):
    """Lazy dict to allow for later additions to DocumentRelease languages."""
    _data = {}

    def __iter__(self):
        return iter(
            DocumentRelease.objects.values_list('lang', flat=True).distinct().order_by('lang')
        )

    def __getitem__(self, key):
        if key not in self._data:
            if not DocumentRelease.objects.filter(lang=key).exists():
                raise KeyError
            self._data[key] = DocsSitemap(key)
        return self._data[key]

    def __len__(self):
        return len(self.keys())

    def __delitem__(key):
        raise NotImplementedError

    def __setitem__(key, value):
        raise NotImplementedError


sitemaps = Sitemaps()

urlpatterns = docs_urlpatterns + [
    url(r'^sitemap\.xml$', sitemap_index, {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>[a-z-]+)\.xml$', sitemap, {'sitemaps': sitemaps},
        name='document-sitemap'),
    url(r'^google79eabba6bf6fd6d3\.html$', lambda req: HttpResponse('google-site-verification: google79eabba6bf6fd6d3.html')),
    # This just exists to make sure we can proof that the error pages work under both hostnames.
    url(r'', include('legacy.urls')),
]
