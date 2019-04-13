from functools import partial
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.crypto import get_random_string


generate_random_string = partial(
    get_random_string,
    length=50,
    allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                  '0123456789!@#$%^&*(-_=+)')


def hub_credentials(hub_url):
    """A callback that returns no credentials, for anonymous
    subscriptions. Meant to be overriden if developers need to
    authenticate with certain hubs"""
    return


def get_hub_credentials(hub_url):
    creds_path = getattr(settings, 'PUSH_CREDENTIALS',
                         'django_push.subscriber.utils.hub_credentials')
    creds_path, creds_function = creds_path.rsplit('.', 1)
    creds_module = import_module(creds_path)
    return getattr(creds_module, creds_function)(hub_url)


def get_domain():
    if hasattr(settings, 'PUSH_DOMAIN'):
        return settings.PUSH_DOMAIN
    elif 'django.contrib.sites' in settings.INSTALLED_APPS:
        from django.contrib.sites.models import Site
        return Site.objects.get_current().domain
    raise ImproperlyConfigured(
        "Unable to deterermine the site's host. Either use "
        "django.contrib.sites and set SITE_ID in your settings or "
        "set PUSH_DOMAIN to your site's domain.")
