import json
import ssl
from decimal import Decimal
from typing import Optional
from urllib.parse import parse_qsl, urlparse, urlunparse
from urllib.request import Request, urlopen

from django.db.transaction import atomic
from django.utils.http import urlencode

from djmoney import settings

from ..models import ExchangeBackend, Rate


try:
    import certifi
except ImportError:
    raise ImportError("Please install dependency certifi - pip install certifi")


class BaseExchangeBackend:
    name: Optional[str] = None
    url: Optional[str] = None

    def get_rates(self, **kwargs):
        """
        Returns a mapping <currency>: <rate>.
        """
        raise NotImplementedError

    def get_url(self, **params):
        """
        Updates base url with provided GET parameters.
        """
        parts = list(urlparse(self.url))
        query = dict(parse_qsl(parts[4]))
        query.update(params)
        parts[4] = urlencode(query)
        return urlunparse(parts)

    def get_params(self):
        """
        Default GET parameters for the request.
        """
        return {}

    def get_response(self, **params):
        headers = {
            "User-Agent": "Mozilla/5.0",
        }
        request = Request(self.get_url(**params), headers=headers)
        context = ssl.create_default_context(cafile=certifi.where())
        response = urlopen(request, context=context)
        return response.read()

    def parse_json(self, response):
        if isinstance(response, bytes):
            response = response.decode("utf-8")
        return json.loads(response, parse_float=Decimal)

    @atomic
    def update_rates(self, base_currency=settings.BASE_CURRENCY, **kwargs):
        """
        Updates rates for the given backend.
        """
        backend, _ = ExchangeBackend.objects.update_or_create(name=self.name, defaults={"base_currency": base_currency})
        backend.clear_rates()
        params = self.get_params()
        params.update(base_currency=base_currency, **kwargs)
        Rate.objects.bulk_create(
            [
                Rate(currency=currency, value=value, backend=backend)
                for currency, value in self.get_rates(**params).items()
            ]
        )


class SimpleExchangeBackend(BaseExchangeBackend):
    """
    Simple backend implementation.
    Assumes JSON response with `rates` key inside.
    """

    def get_rates(self, **params):
        response = self.get_response(**params)
        return self.parse_json(response)["rates"]
