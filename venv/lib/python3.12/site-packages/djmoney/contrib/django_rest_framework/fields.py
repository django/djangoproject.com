from django.core.exceptions import FieldDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

from rest_framework.fields import empty
from rest_framework.serializers import DecimalField, ModelSerializer

from djmoney.models.fields import MoneyField as ModelField
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator
from djmoney.money import Money
from djmoney.utils import MONEY_CLASSES, get_currency_field_name
from moneyed.classes import CurrencyDoesNotExist


class _PrimitiveMoney:
    """
    A container for ``Money`` data that does not do any validation of said data.
    It conveniently holds the amount and currency attributes to ease transformation into a valid ``Money`` instance.
    """

    __slots__ = ("amount", "currency")

    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency


class MoneyField(DecimalField):
    """
    Treats ``Money`` objects as decimal values in representation and
    does decimal's validation during transformation to native value.
    """

    default_error_messages = {
        "invalid_currency": _("{currency!r} is not a valid currency"),
    }

    def __init__(self, *args, **kwargs):
        self.default_currency = kwargs.pop("default_currency", None)
        super().__init__(*args, **kwargs)
        # Rest Framework converts `min_value` / `max_value` to validators, that are not aware about `Money` class
        # We need to adjust them
        for idx, validator in enumerate(self.validators):
            if isinstance(validator, MinValueValidator):
                self.validators[idx] = MinMoneyValidator(self.min_value)
            elif isinstance(validator, MaxValueValidator):
                self.validators[idx] = MaxMoneyValidator(self.max_value)

    def to_representation(self, obj):
        """
        When ``field_currency`` is not in ``self.validated_data`` then ``obj`` is an instance of ``Decimal``, otherwise
        it is ``Money``.
        """
        if isinstance(obj, MONEY_CLASSES):
            obj = obj.amount
        return super().to_representation(obj)

    def to_internal_value(self, data):
        if isinstance(data, MONEY_CLASSES + (_PrimitiveMoney,)):
            amount = super().to_internal_value(data.amount)
            try:
                return Money(amount, data.currency)
            except CurrencyDoesNotExist:
                self.fail("invalid_currency", currency=data.currency)

        return super().to_internal_value(data)

    def get_value(self, data):
        parent_meta = getattr(self.parent, "Meta", None)

        default_currency = self.default_currency

        if parent_meta and hasattr(parent_meta, "model"):
            model = self.parent.Meta.model
            try:
                field = model._meta.get_field(self.source)
                default_currency = field.default_currency
            except FieldDoesNotExist as e:
                if not hasattr(model, self.source):
                    raise ValueError(
                        f"{self.source} is neither a db field nor a property on the model {model.__name__}"
                    ) from e

        amount = super().get_value(data)
        currency = data.get(get_currency_field_name(self.field_name), self.default_currency or default_currency)
        if currency and amount is not None and not isinstance(amount, MONEY_CLASSES) and amount is not empty:
            return _PrimitiveMoney(amount=amount, currency=currency)
        return amount


def register_money_field():
    ModelSerializer.serializer_field_mapping[ModelField] = MoneyField
