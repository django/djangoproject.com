from django.contrib.sitemaps import Sitemap

from .models import Document


class DocsSitemap(Sitemap):
    def __init__(self, lang):
        self.lang = lang

    def items(self):
        return (Document.objects.filter(release__lang=self.lang)
                .order_by('-release__release', 'path')
                .select_related('release__release'))

    def changefreq(self, obj):
        return 'daily'
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

    def _urls(self, page, site, protocol):
        # XXX: To workaround bad interaction between contrib.sitemaps and
        # django-hosts (scheme/domain would be repeated twice in URLs)
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
