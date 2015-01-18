from decimal import Decimal

from django import template
from django.template.defaultfilters import floatformat


register = template.Library()


@register.filter
def as_percentage(part, total):
    if total is None or part is None:
        return "0.00"

    try:
        return floatformat((part / total) * Decimal("100.0"))
    except ZeroDivisionError:
        return "0.00"
