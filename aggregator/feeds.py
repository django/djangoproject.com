from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_hosts.resolvers import reverse

from .models import FeedItem, FeedType


class BaseCommunityAggregatorFeed(Feed):
    def items(self):
        return FeedItem.objects.approved().order_by("-date_modified")

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


class CommunityAggregatorFeed(BaseCommunityAggregatorFeed):
    def get_object(self, request, slug=None):
        return get_object_or_404(FeedType, slug=slug)

    def items(self, obj):
        qs = super().items()
        qs = qs.filter(feed__feed_type=obj)
        qs = qs.select_related("feed", "feed__feed_type")
        return qs[:25]

    def title(self, obj):
        return _("Django community aggregator: %s") % obj.name

    def link(self, obj):
        return reverse("aggregator-feed", args=[obj.slug], host="www")

    def description(self, obj):
        return self.title(obj)


class CommunityAggregatorFirehoseFeed(BaseCommunityAggregatorFeed):
    title = _("Django community aggregator firehose")
    description = _("All activity from the Django community aggregator")

    def link(self):
        return reverse("aggregator-firehose-feed", host="www")

    def items(self):
        qs = super().items()
        qs = qs.select_related("feed")
        return qs[:50]
