from django.core import rss
from django.models.blog import entries

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

rss.register_feed(weblog_entry_feed)
