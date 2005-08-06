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
        parsed_feed = feedparser.parse(feed.feed_url)
        for entry in parsed_feed.entries:
            title = entry.title.encode(parsed_feed.encoding, "xmlcharrefreplace")
            guid = entry.get("id", entry.link).encode(parsed_feed.encoding, "xmlcharrefreplace")
            link = entry.link.encode(parsed_feed.encoding, "xmlcharrefreplace")
            if hasattr(entry, "summary"):
                content = entry.summary
            elif hasattr(entry, "content"):
                content = entry.content[0].value
            elif hasattr(entry, "description"):
                content = entry.description
            else:
                content = u""
            content = content.encode(parsed_feed.encoding, "xmlcharrefreplace")
            date_modified = datetime.datetime.fromtimestamp(time.mktime(entry.modified_parsed))
            try:
                feeditem = feed.get_feeditem(guid__exact=guid)
            except feeditems.FeedItemDoesNotExist:
                feeditem = feed.add_feeditem(title=title,
                                             link=link,
                                             summary=content,
                                             guid=guid,
                                             date_modified=date_modified)
            else:
                feeditem.date_modified = date_modified
                feeditem.save()

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--settings')
    options, args = parser.parse_args()
    if options.settings:
        os.environ["DJANGO_SETTINGS_MODULE"] = options.settings
    update_feeds()