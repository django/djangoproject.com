from django.contrib.syndication.feeds import Feed
from django_website.apps.aggregator.models import FeedItem

class CommunityAggregatorFeed(Feed):
    title = "The Django community aggregator"
    link = "http://www.djangoproject.com/community/"
    description = "Aggregated feeds from the Django community."

    def items(self):
        return FeedItem.objects.all()[:10]
