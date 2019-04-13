import requests

from django.conf import settings

from .. import UA


def ping_hub(feed_url, hub_url=None):
    """
    Makes a POST request to the hub. If no hub_url is provided, the
    value is fetched from the PUSH_HUB setting.

    Returns a `requests.models.Response` object.
    """
    if hub_url is None:
        hub_url = getattr(settings, 'PUSH_HUB', None)
    if hub_url is None:
        raise ValueError("Specify hub_url or set the PUSH_HUB setting.")
    params = {
        'hub.mode': 'publish',
        'hub.url': feed_url,
    }
    return requests.post(hub_url, data=params, headers={'User-Agent': UA})
