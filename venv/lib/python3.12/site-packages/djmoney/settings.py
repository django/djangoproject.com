import operator
from types import MappingProxyType
from typing import Optional

from django.conf import settings

from moneyed import CURRENCIES, XXX, Currency


# The default currency, you can define this in your project's settings module
# This has to be a currency object imported from moneyed
DEFAULT_CURRENCY: Optional[Currency] = getattr(settings, "DEFAULT_CURRENCY", None)


# The default currency choices, you can define this in your project's
# settings module
PROJECT_CURRENCIES = getattr(settings, "CURRENCIES", None)
CURRENCY_CHOICES = getattr(settings, "CURRENCY_CHOICES", None)

if CURRENCY_CHOICES is None:
    if PROJECT_CURRENCIES:
        CURRENCY_CHOICES = [(code, CURRENCIES[code].name) for code in PROJECT_CURRENCIES]
    else:
        # 'XXX' is a backport from py-moneyed for transactions involving no currency;
        # this was previously referred to as moneyed.classes.DEFAULT_CURRENCY_CODE
        CURRENCY_CHOICES = [(c.code, c.name) for i, c in CURRENCIES.items() if c != XXX]

CURRENCY_CHOICES.sort(key=operator.itemgetter(1, 0))
DECIMAL_PLACES = getattr(settings, "CURRENCY_DECIMAL_PLACES", 2)

OPEN_EXCHANGE_RATES_URL = getattr(settings, "OPEN_EXCHANGE_RATES_URL", "https://openexchangerates.org/api/latest.json")
OPEN_EXCHANGE_RATES_APP_ID = getattr(settings, "OPEN_EXCHANGE_RATES_APP_ID", None)
FIXER_URL = getattr(settings, "FIXER_URL", "http://data.fixer.io/api/latest")
FIXER_ACCESS_KEY = getattr(settings, "FIXER_ACCESS_KEY", None)
BASE_CURRENCY = getattr(settings, "BASE_CURRENCY", "USD")
EXCHANGE_BACKEND = getattr(settings, "EXCHANGE_BACKEND", "djmoney.contrib.exchange.backends.OpenExchangeRatesBackend")
RATES_CACHE_TIMEOUT = getattr(settings, "RATES_CACHE_TIMEOUT", 600)

CURRENCY_CODE_MAX_LENGTH = getattr(settings, "CURRENCY_CODE_MAX_LENGTH", 3)

MONEY_FORMAT = MappingProxyType(getattr(settings, "MONEY_FORMAT", {}))
