from django.core.exceptions import ImproperlyConfigured

from djmoney import settings

from .base import SimpleExchangeBackend


class FixerBackend(SimpleExchangeBackend):
    name = "fixer.io"

    def __init__(self, url=settings.FIXER_URL, access_key=settings.FIXER_ACCESS_KEY):
        if access_key is None:
            raise ImproperlyConfigured("settings.FIXER_ACCESS_KEY should be set to use FixerBackend")
        self.url = url
        self.access_key = access_key

    def get_params(self):
        # support both `data.fixer.io` and `api.apilayer.com` auth params
        return {
            "apikey": self.access_key,
            "access_key": self.access_key,
        }
