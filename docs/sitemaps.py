from django.contrib.sitemaps import Sitemap

from djangoproject.sitemaps import LocationAbsoluteUrlMixin

from .models import Document
from .search import DocumentationCategory


class DocsSitemap(LocationAbsoluteUrlMixin, Sitemap):
    def __init__(self, lang):
        self.lang = lang

    def items(self):
        return (
            Document.objects.filter(release__lang=self.lang)
            .exclude(metadata__parents=DocumentationCategory.WEBSITE)
            .order_by("-release__release", "path")
            .select_related("release__release")
        )

    def location(self, item):
        return item.get_absolute_url()

    def changefreq(self, obj):
        return "daily"

    #        if obj.release.is_dev:
    #            return 'daily'
    #        elif obj.release.is_default:
    #            return 'monthly'
    #        else:
    #            return 'yearly'

    def priority(self, obj):
        if obj.release.is_dev:
            return 0.5
        elif obj.release.is_default:
            return 1
        else:
            return 0.1
