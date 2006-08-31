from django.contrib.sitemaps import Sitemap
from django_website.apps.blog.models import Entry
from django_website.apps.docs.models import Document
from django.contrib.flatpages.models import FlatPage
import datetime

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
        return Entry.objects.filter(pub_date__lte=datetime.datetime.now())

    # lastmod is not implemented, because weblog pages contain comments.
    # We'd rather not look up the date of the latest comment -- not worth the overhead.

class DocumentationSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Document.objects.all()

    # lastmod is not implemented, because documentation contains comments.
    # We'd rather not look up the date of the latest comment -- not worth the overhead.
