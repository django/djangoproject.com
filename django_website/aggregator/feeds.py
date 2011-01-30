from __future__ import absolute_import

from django.core import urlresolvers
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from .models import FeedType, FeedItem

class CommunityAggregatorFeed(Feed):
    description = "Aggregated feeds from the Django community."

    def get_object(self, request, slug=None):
        if slug:
            return get_object_or_404(FeedType, slug=slug)
        return None

    def title(self, obj):
        title = obj.name if obj else "firehose"
        return "Django community aggregator: %s" % title

    def link(self, obj):
        if obj:
            return urlresolvers.reverse('aggregator-feed', args=[obj.slug])
        else:
            return urlresolvers.reverse('aggregator-firehose-feed')

    def description(self, obj):
        return self.title(obj)

    def items(self, obj):
        qs = FeedItem.objects.order_by('-date_modified')
        qs = qs.select_related('feed', 'feed__feed_type')
        if obj:
            qs = qs.filter(feed__feed_type=obj)
        return qs[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary

    def item_guid(self, item):
        return item.guid

    def item_link(self, item):
        return item.link

    def item_author_name(self, item):
        return item.feed.title

    def item_author_link(self, item):
        return item.feed.public_url

    def item_pubdate(self, item):
        return item.date_modified
