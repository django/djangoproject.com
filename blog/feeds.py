from django.contrib.syndication.views import Feed
from django.utils.translation import gettext_lazy as _

from .models import Entry


class WeblogEntryFeed(Feed):
    title = _("The Django weblog")
    link = "https://www.djangoproject.com/weblog/"
    description = _("Latest news about Django, the Python web framework.")

    def items(self):
        return Entry.objects.published()[:10]

    def item_pubdate(self, item):
        return item.pub_date

    def item_author_name(self, item):
        return item.author

    def item_description(self, item):
        return item.body_html
