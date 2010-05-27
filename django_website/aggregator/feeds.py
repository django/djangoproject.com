from __future__ import absolute_import

from django.contrib.syndication.views import Feed
from .models import FeedItem

class CommunityAggregatorFeed(Feed):
    title = "The Django community aggregator"
    link = "http://www.djangoproject.com/community/"
    description = "Aggregated feeds from the Django community."

    def items(self):
        return FeedItem.objects.all()[:10]
