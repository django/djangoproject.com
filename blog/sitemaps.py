from __future__ import absolute_import

from django.contrib.sitemaps import Sitemap

from .models import Entry

class WeblogSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.4

    def items(self):
        return Entry.objects.published()

    # lastmod wasn't implemented, because weblog pages used to contain comments.

