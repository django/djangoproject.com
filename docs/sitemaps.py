from django.contrib.sitemaps import Sitemap

from .models import Document


class DocsSitemap(Sitemap):

    def items(self):
        return (Document.objects
                .order_by('release__lang', '-release__release', 'path')
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

    def get_urls(self, page, site, protocol):
        urls = []
        for item in self.paginator.page(page).object_list:
            loc = item.get_absolute_url()
            priority = self.priority(item)
            url_info = {
                'item': item,
                'location': loc,
                'changefreq': self.changefreq(item),
                'priority': str(priority if priority is not None else ''),
            }
            urls.append(url_info)
        return urls
