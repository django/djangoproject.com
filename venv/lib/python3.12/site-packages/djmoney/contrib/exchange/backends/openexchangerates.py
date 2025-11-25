from django.core.exceptions import ImproperlyConfigured

from djmoney import settings

from .base import SimpleExchangeBackend


class OpenExchangeRatesBackend(SimpleExchangeBackend):
    name = "openexchangerates.org"
    url = settings.OPEN_EXCHANGE_RATES_URL

    def __init__(self, url=settings.OPEN_EXCHANGE_RATES_URL, access_key=settings.OPEN_EXCHANGE_RATES_APP_ID):
        if access_key is None:
            raise ImproperlyConfigured(
                "settings.OPEN_EXCHANGE_RATES_APP_ID should be set to use OpenExchangeRatesBackend"
            )
        self.url = url
        self.access_key = access_key

    def get_params(self):
        return {"app_id": self.access_key, "base": settings.BASE_CURRENCY}
