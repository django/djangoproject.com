from django.core import rss
from django.models.blog import entries
from django.models.comments import freecomments
from django.models.aggregator import feeditems

weblog_entry_feed = rss.FeedConfiguration(
    slug = 'weblog',
    title_cb = lambda param: "The Django weblog",
    link_cb = lambda param: "http://www.djangoproject.com/weblog/",
    description_cb = lambda param: "Latest news about Django, the Python Web framework.",
    get_list_func_cb = lambda obj: entries.get_list,
    get_list_kwargs = {
        'limit': 10,
    }
)

recent_comments = rss.FeedConfiguration(
    slug = 'comments',
    title_cb = lambda param: "Recent comments on djangoproject.com",
    link_cb = lambda param: "http://www.djangoproject.com/comments/",
    description_cb = lambda param: "Recent comments posted to djangoproject.com.",
    get_list_func_cb = lambda obj: freecomments.get_list,
    get_list_kwargs = {
        'limit': 15,
    }
)

community_aggregator = rss.FeedConfiguration(
    slug = 'community',
    title_cb = lambda param: "The Django community aggregator",
    link_cb = lambda param: "http://www.djangoproject.com/community/",
    description_cb = lambda param: "Aggregated feeds from the Django community.",
    get_list_func_cb = lambda obj: feeditems.get_list,
    get_list_kwargs = {
        'limit' :  10,
    }
)

rss.register_feed(recent_comments)
rss.register_feed(weblog_entry_feed)
rss.register_feed(community_aggregator)