import socket
import urllib2
from django.core.management.base import BaseCommand
from django_website.aggregator.models import Feed

class Command(BaseCommand):
    """
    Mark people with 404'ing feeds as defunct.
    """
    def handle(self, *args, **kwargs):
        for f in Feed.objects.filter(is_defunct=False):
            try:
                r = urllib2.urlopen(f.feed_url, timeout=15)
            except (urllib2.HTTPError, urllib2.URLError, socket.timeout), e:
                print "%s on '%s'; marking defunct" % (e, f)
                f.is_defunct = True
                f.save()