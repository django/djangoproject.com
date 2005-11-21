from django.contrib.syndication.feeds import Feed
from django.models.aggregator import feeditems

class CommunityAggregatorFeed(Feed):
    title = "The Django community aggregator"
    link = "http://www.djangoproject.com/community/"
    description = "Aggregated feeds from the Django community."
    
    def items(self):
        return feeditems.get_list(limit=10)
