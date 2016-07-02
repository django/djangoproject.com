import requests
from django.core.cache import cache
from requests.exceptions import RequestException

PEOPLE_STATS_URL = 'https://people.djangoproject.com/api/stats/'
PACKAGES_STATS_URL = 'https://www.djangopackages.com/api/v3/packages/?limit=0'
STATS_CACHE_KEY = 'community_stats'


def fetch(url):
    try:
        return requests.get(url, timeout=0.5).json()
    except (RequestException, ValueError):
        return {}


def community_stats(request):
    """
    Context processor to fetch community stats from Django people and
    Django packages.

    This caches the resulting dictionary to lower the chance
    of overwhelming those services.
    """
    stats = cache.get(STATS_CACHE_KEY, None)
    if not stats:

        stats = fetch(PEOPLE_STATS_URL)
        packages_data = fetch(PACKAGES_STATS_URL)
        if 'meta' in packages_data:
            stats.update({'packages': packages_data['meta']['total_count']})

        stats = {'community_stats': stats}

        cache.add(STATS_CACHE_KEY, stats, 60 * 60 * 12)  # for half a day

    return stats
