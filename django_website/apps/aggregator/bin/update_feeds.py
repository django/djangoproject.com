"""
Update feeds for Django community page.  Requires Mark Pilgrim's excellent 
Universal Feed Parser (http://feedparser.org)
"""

import os
import time
import optparse
import datetime
import feedparser

def update_feeds():
    from django.models.aggregator import feeds, feeditems
    for feed in feeds.get_iterator(is_defunct__exact=False):
        for entry in feedparser.parse(feed.feed_url).entries:
            try:
                feeditem = feed.get_feeditem(guid__exact=str(entry.id))
            except feeditems.FeedItemDoesNotExist:
                for i in ("summary", "content", "description"):
                    summary = entry.get(i, "")
                    if summary: break
                feeditem = feed.add_feeditem(title=str(entry.title),
                                             link=str(entry.link),
                                             summary=str(summary),
                                             guid=str(entry.get("id", entry.link)),
                                             date_modified=datetime.datetime.fromtimestamp(time.mktime(entry.modified_parsed)))
            else:
                feeditem.date_modified = datetime.datetime.fromtimestamp(time.mktime(entry.modified_parsed))
                feeditem.save()

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--settings')
    options, args = parser.parse_args()
    if options.settings:
        os.environ["DJANGO_SETTINGS_MODULE"] = options.settings
    update_feeds()