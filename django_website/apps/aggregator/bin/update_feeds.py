"""
Update feeds for Django community page.  Requires Mark Pilgrim's excellent
Universal Feed Parser (http://feedparser.org)
"""

import os
import sys
import time
import socket
import optparse
import datetime
import feedparser

LOCKFILE = "/tmp/update_feeds.lock"
def update_feeds(verbose=False):
    from django_website.apps.aggregator.models import Feed, FeedItem
    for feed in Feed.objects.filter(is_defunct=False):
        if verbose:
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

def main(argv):
    socket.setdefaulttimeout(15)
    parser = optparse.OptionParser()
    parser.add_option('--settings')
    parser.add_option('-v', '--verbose', action="store_true")
    options, args = parser.parse_args(argv)
    if options.settings:
        os.environ["DJANGO_SETTINGS_MODULE"] = options.settings
    update_feeds(options.verbose)

if __name__ == '__main__':
    try:
        lockfile = os.open(LOCKFILE, os.O_CREAT | os.O_EXCL)
    except OSError:
        sys.exit(0)
    try:
        sys.exit(main(sys.argv))
    finally:
        os.close(lockfile)
        os.unlink(LOCKFILE)        
