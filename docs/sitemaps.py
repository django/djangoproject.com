from django.contrib.sitemaps import Sitemap

from .models import Document


class DocsSitemap(Sitemap):

    def items(self):
        return (Document.objects
                .order_by('release__lang', '-release__version', 'path')
                .select_related('release'))

    def changefreq(self, obj):
        if obj.release.is_dev:
            return 'daily'
        elif obj.release.is_default:
            return 'monthly'
        else:
            return 'yearly'

    def priority(self, obj):
        if obj.release.is_dev:
            return 0.5
        elif obj.release.is_default:
            return 1
        else:
            return 0.1
