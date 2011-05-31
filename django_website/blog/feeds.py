from __future__ import absolute_import

from django.contrib.syndication.views import Feed
from .models import Entry

class WeblogEntryFeed(Feed):
    title = "The Django weblog"
    link = "http://www.djangoproject.com/weblog/"
    description = "Latest news about Django, the Python Web framework."

    def items(self):
        return Entry.objects.published()[:10]

    def item_pubdate(self, item):
        return item.pub_date
