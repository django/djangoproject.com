from django.db.models import F
from django.db.models.expressions import BaseExpression

from djmoney.money import Money
from moneyed import Money as OldMoney


MONEY_CLASSES = (Money, OldMoney)


def get_currency_field_name(name, field=None):
    if field and getattr(field, "currency_field_name", None):
        return field.currency_field_name
    return "%s_currency" % name


def get_amount(value):
    """
    Extracts decimal value from Money or Expression.
    """
    if isinstance(value, MONEY_CLASSES):
        return value.amount
    elif isinstance(value, BaseExpression) and not isinstance(value, F):
        return get_amount(value.value)
    return value


def prepare_expression(expr):
    """
    Prepares some complex money expression to be used in query.
    """
    if isinstance(expr.rhs, F):
        # Money(...) + F('money')
        target, return_value = expr.lhs, expr.rhs
    else:
        # F('money') + Money(...)
        target, return_value = expr.rhs, expr.lhs
    amount = get_amount(target)
    target.value = amount
    return return_value
