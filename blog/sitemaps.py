from django.contrib.sitemaps import Sitemap

from .models import Entry


class WeblogSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.4

    def items(self):
        return Entry.objects.published()

    def get_urls(self, page, site, protocol):
        urls = []
        for item in self.paginator.page(page).object_list:
            loc = item.get_absolute_url()
            url_info = {
                'item': item,
                'location': loc,
            }
            urls.append(url_info)
        return urls

    # lastmod wasn't implemented, because weblog pages used to contain comments.
