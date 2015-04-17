from django.core.cache import cache
from django.utils import crypto

GENERATION_KEY_NAME = 'metric:generation'


def generation_key(timeout=60 * 60 * 24 * 365):
    """
    A random key to be used in cache calls that allows
    invalidating all values created with it. Use it with
    the version parameter of cache.get/set.
    """
    generation = cache.get(GENERATION_KEY_NAME)
    if generation is None:
        generation = crypto.get_random_string(length=12)
        cache.set(GENERATION_KEY_NAME, generation, timeout)
    return generation


def reset_generation_key():
    """
    Invalidate all cache entries created with the generation key.
    """
    cache.delete(GENERATION_KEY_NAME)
