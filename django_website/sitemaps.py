from __future__ import absolute_import

from django.contrib.sitemaps import Sitemap
from django.contrib.flatpages.models import FlatPage

class FlatPageSitemap(Sitemap):
    """
    We're not using the built-in django.contrib.sitemaps.FlatPageSitemap,
    because we're doing something different. Also, we only have one Site,
    so there's no need to check the site is current.
    """
    def changefreq(self, obj):
        if obj.url.startswith('/documentation/0_90/') or obj.url.startswith('/documentation/0_91/'):
            return 'never' # Old documentation never changes.
        else:
            return 'weekly'

    def priority(self, obj):
        if obj.url.startswith('/documentation/0_90/') or obj.url.startswith('/documentation/0_91/'):
            return 0.1 # Old documentation gets a low priority.
        else:
            return 0.5

    def items(self):
        return FlatPage.objects.all()

    # lastmod is not implemented, because we have no way of knowing
    # when FlatPages were last updated.
