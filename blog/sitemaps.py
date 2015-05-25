from django.contrib.sitemaps import Sitemap

from .models import Entry


class WeblogSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.4

    def items(self):
        return Entry.objects.published()

    # lastmod wasn't implemented, because weblog pages used to contain comments.

    # XXX: Hack to fix bad interaction with contrib.sitemaps and django-hosts
    def _urls(self, page, protocol, domain):
        return super(WeblogSitemap, self)._urls(page, protocol, domain='')
