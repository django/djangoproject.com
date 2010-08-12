import urllib2
from django.core.management.base import BaseCommand
from django_website.apps.aggregator.models import Feed

class Command(BaseCommand):
    """
    Mark people with 404'ing feeds as defunct.
    """
    def handle(self, *args, **kwargs):
        for f in Feed.objects.all():
            try:
                r = urllib2.urlopen(f.feed_url)
            except urllib2.HTTPError, e:
                if e.code == 404 or e.code == 500:
                    print "%s on %s; marking defunct" % (e.code, f)
                    f.is_defunct = True
                    f.save()
                else:
                    raise
