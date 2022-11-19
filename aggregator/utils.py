from django.conf import settings

from .models import FeedItem, FeedType


def push_credentials(hub_url):
    """
    Callback for django_push to get a hub's credentials.

    We always use superfeedr so this is easy.
    """
    return tuple(settings.SUPERFEEDR_CREDS)


def get_feed_data(num_items=5) -> list:
    """ Fetches feed data, from cache if available """
    feeds = []
    feed_types = FeedType.objects.values('id', 'name', 'slug', 'can_self_add')
    for ft in feed_types:
        feeds.append((ft, FeedItem.cached_by_feed_type_id(ft['id'])[0:num_items]))
    return feeds
