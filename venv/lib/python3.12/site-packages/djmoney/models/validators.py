from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.translation import gettext_lazy as _

from djmoney.money import Money


class BaseMoneyValidator(BaseValidator):
    def get_limit_value(self, cleaned):
        if isinstance(self.limit_value, Money):
            if cleaned.currency.code != self.limit_value.currency.code:
                return
            return self.limit_value
        elif isinstance(self.limit_value, (int, Decimal)):
            return self.limit_value
        try:
            return Money(self.limit_value[cleaned.currency.code], cleaned.currency.code)
        except KeyError:
            # There are no validation for this currency
            pass

    def __call__(self, value):
        cleaned = self.clean(value)
        limit_value = self.get_limit_value(cleaned)
        if limit_value is None:
            return
        if isinstance(limit_value, (int, Decimal)):
            cleaned = cleaned.amount
        params = {"limit_value": limit_value, "show_value": cleaned, "value": value}
        if self.compare(cleaned, limit_value):
            raise ValidationError(self.message, code=self.code, params=params)


# The validators below are not inherited from Django's validators because of
# subclass check in Django REST Framework, that removes all validators
# from the serializer field except the first one in the `validators` list of each validator type (min / max)
# Removing inheritance is the simplest option to make model validators work in REST Framework


class MinMoneyValidator(BaseMoneyValidator):
    message = _("Ensure this value is greater than or equal to %(limit_value)s.")
    code = "min_value"

    def compare(self, a, b):
        return a < b


class MaxMoneyValidator(BaseMoneyValidator):
    message = _("Ensure this value is less than or equal to %(limit_value)s.")
    code = "max_value"

    def compare(self, a, b):
        return a > b
