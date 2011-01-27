import datetime
import feedparser
import optparse
import os
import socket
import sys
import time
import threading
import Queue
from django.core.management.base import BaseCommand
from django_website.aggregator.models import Feed, FeedItem

class Command(BaseCommand):
    """
    Update feeds for Django community page.  Requires Mark Pilgrim's excellent
    Universal Feed Parser (http://feedparser.org)
    """
    LOCKFILE = "/tmp/update_feeds.lock"
    
    option_list = BaseCommand.option_list + (
        optparse.make_option('-t', '--threads',
            metavar='NUM',
            type='int',
            default=4,
            help='Number of updater threads (default: 4).'
        ),
    )

    def handle(self, *args, **kwargs):
        try:
            lockfile = os.open(self.LOCKFILE, os.O_CREAT | os.O_EXCL)
        except OSError:
            print >> sys.stderr, "Lockfile exists (%s). Aborting." % self.LOCKFILE
            sys.exit(1)

        try:
            verbose = kwargs.get('verbosity')
            socket.setdefaulttimeout(15)
            self.update_feeds(verbose=verbose, num_threads=kwargs['threads'])
        except:
            sys.exit(1)
        finally:
            os.close(lockfile)
            os.unlink(self.LOCKFILE)

    def update_feeds(self, verbose=False, num_threads=4):
        feed_queue = Queue.Queue()
        for feed in Feed.objects.filter(is_defunct=False):
            feed_queue.put(feed)

        threadpool = []
        for i in range(num_threads):
            threadpool.append(FeedUpdateWorker(feed_queue, verbose))
            
        [t.start() for t in threadpool]
        [t.join() for t in threadpool]

class FeedUpdateWorker(threading.Thread):
    
    def __init__(self, q, verbose, **kwargs):
        super(FeedUpdateWorker, self).__init__(**kwargs)
        self.verbose = verbose
        self.q = q
        
    def run(self):
        while 1:
            try:
                feed = self.q.get_nowait()
            except Queue.Empty:
                return
            self.update_feed(feed)
            self.q.task_done()
            
    def update_feed(self, feed):
        if self.verbose:
            print feed
        
        parsed_feed = feedparser.parse(feed.feed_url)
        for entry in parsed_feed.entries:
            title = entry.title.encode(parsed_feed.encoding, "xmlcharrefreplace")
            guid = entry.get("id", entry.link).encode(parsed_feed.encoding, "xmlcharrefreplace")
            link = entry.link.encode(parsed_feed.encoding, "xmlcharrefreplace")

            if not guid:
                guid = link

            if hasattr(entry, "summary"):
                content = entry.summary
            elif hasattr(entry, "content"):
                content = entry.content[0].value
            elif hasattr(entry, "description"):
                content = entry.description
            else:
                content = u""
            content = content.encode(parsed_feed.encoding, "xmlcharrefreplace")

            try:
                if entry.has_key('modified_parsed'):
                    date_modified = datetime.datetime.fromtimestamp(time.mktime(entry.modified_parsed))
                elif parsed_feed.feed.has_key('modified_parsed'):
                    date_modified = datetime.datetime.fromtimestamp(time.mktime(parsed_feed.feed.modified_parsed))
                elif parsed_feed.has_key('modified'):
                    date_modified = datetime.datetime.fromtimestamp(time.mktime(parsed_feed.modified))
                else:
                    date_modified = datetime.datetime.now()
            except TypeError:
                date_modified = datetime.datetime.now()

            try:
                feed.feeditem_set.get(guid=guid)
            except FeedItem.DoesNotExist:
                feed.feeditem_set.create(title=title, link=link, summary=content, guid=guid, date_modified=date_modified)
