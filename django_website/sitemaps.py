from __future__ import absolute_import

import datetime
from django.contrib.sitemaps import Sitemap
from django.contrib.flatpages.models import FlatPage

from blog.models import Entry

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

class WeblogSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.4

    def items(self):
        return Entry.objects.published()

    # lastmod is not implemented, because weblog pages contain comments.
    # We'd rather not look up the date of the latest comment -- not worth the overhead.

