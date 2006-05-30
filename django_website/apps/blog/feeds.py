from django.contrib.syndication.feeds import Feed
from django_website.apps.blog.models import Entry

class WeblogEntryFeed(Feed):
    title = "The Django weblog"
    link = "http://www.djangoproject.com/weblog/"
    description = "Latest news about Django, the Python Web framework."

    def items(self):
        return Entry.objects.all()[:10]
