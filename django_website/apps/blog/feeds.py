from django.contrib.syndication.feeds import Feed
from django.models.blog import entries

class WeblogEntryFeed(Feed):
    title = "The Django weblog"
    link = "http://www.djangoproject.com/weblog/"
    description = "Latest news about Django, the Python Web framework."
    
    def items(self):
        return entries.get_list(limit=10)

