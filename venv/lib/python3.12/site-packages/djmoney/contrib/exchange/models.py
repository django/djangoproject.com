from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.module_loading import import_string

from djmoney.settings import CURRENCY_CODE_MAX_LENGTH, EXCHANGE_BACKEND, RATES_CACHE_TIMEOUT

from .exceptions import MissingRate


class ExchangeBackend(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    last_update = models.DateTimeField(auto_now=True)
    base_currency = models.CharField(max_length=CURRENCY_CODE_MAX_LENGTH)

    def __str__(self):
        return self.name

    def clear_rates(self):
        self.rates.all().delete()


class Rate(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")
    currency = models.CharField(max_length=CURRENCY_CODE_MAX_LENGTH)
    value = models.DecimalField(max_digits=20, decimal_places=6)
    backend = models.ForeignKey(ExchangeBackend, on_delete=models.CASCADE, related_name="rates")

    class Meta:
        unique_together = (("currency", "backend"),)


def get_default_backend_name():
    return import_string(EXCHANGE_BACKEND).name


def get_rate(source, target, backend=None):
    """
    Returns an exchange rate between source and target currencies.
    Converts exchange rate on the DB side if there is no backends with given base currency.
    Uses data from the default backend if the backend is not specified.
    """
    if str(source) == str(target):
        return 1
    if backend is None:
        backend = get_default_backend_name()
    key = f"djmoney:get_rate:{source}:{target}:{backend}"
    result = cache.get(key)
    if result is not None:
        return result
    result = _get_rate(source, target, backend)
    cache.set(key, result, RATES_CACHE_TIMEOUT)
    return result


def _get_rate(source, target, backend):
    source, target = str(source), str(target)
    rates = Rate.objects.filter(currency__in=(source, target), backend=backend).select_related("backend")
    if not rates:
        raise MissingRate(f"Rate {source} -> {target} does not exist")
    if len(rates) == 1:
        return _try_to_get_rate_directly(source, target, rates[0])
    return _get_rate_via_base(rates, target)


def _try_to_get_rate_directly(source, target, rate):
    """
    Either target or source equals to base currency of existing rate.
    """
    # Converting from base currency to target
    if rate.backend.base_currency == source and rate.currency == target:
        return rate.value
    # Converting from target currency to base
    elif rate.backend.base_currency == target and rate.currency == source:
        return 1 / rate.value
    # Case when target or source is not a base currency
    raise MissingRate(f"Rate {source} -> {target} does not exist")


def _get_rate_via_base(rates, target):
    """
    :param: rates: A set/tuple of two base Rate instances
    :param: target: A string instance of the currency to convert to

    Both target and source are not a base currency - actual rate could be calculated via their rates to base currency.
    For example:

    7.84 NOK = 1 USD = 8.37 SEK

    7.84 NOK = 8.37 SEK

    1 NOK = 8.37 / 7.84 SEK
    """
    first, second = rates
    # Instead of expecting an explicit order in the `rates` iterable, that will put the
    # source currency in the first place, we decided to add an extra check here and swap
    # items if they are ordered not as expected
    if first.currency == target:
        first, second = second, first
    return second.value / first.value


def convert_money(value, currency):
    if "djmoney.contrib.exchange" not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured(
            "You have to add 'djmoney.contrib.exchange' to INSTALLED_APPS in order to use currency exchange"
        )
    amount = value.amount * get_rate(value.currency, currency)
    return value.__class__(amount, currency)
