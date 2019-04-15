from decimal import ROUND_HALF_EVEN

from django import template
import moneyed
from moneyed.localization import _format, format_money, _sign


register = template.Library()


# The default currency formatting of py-moneyed/djmoney doesn't do
# what we want, so we set up a custom one here, applying a consistent
# format that always prefixes the three-letter currency code and
# symbol.
DJANGO = "django"

_format(DJANGO, group_size=3, group_separator=",", decimal_point=".",
        positive_sign="", trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)

# The DSF mostly only deals in USD with occasional grants iN EUR, but
# we set up a few other currencies here just to be safe.
#
# Any currencies not defined here will fall back to the py-moneyed
# default formatter.
_sign(DJANGO, moneyed.AUD, prefix='AUD $')
_sign(DJANGO, moneyed.CAD, prefix='CAD $')
_sign(DJANGO, moneyed.EUR, prefix='EUR €')
_sign(DJANGO, moneyed.GBP, prefix='GBP £')
_sign(DJANGO, moneyed.JPY, prefix='JPY ¥')
_sign(DJANGO, moneyed.NZD, prefix='NZD $')
_sign(DJANGO, moneyed.USD, prefix='USD $')


@register.filter
def currency(value):
    return format_money(value, locale=DJANGO)
