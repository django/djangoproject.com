from datetime import date

from django import template
from django.template.defaultfilters import date as datefilter

register = template.Library()


@register.simple_tag
def isodate(datestr, dateformat="DATE_FORMAT"):
    """
    Convert the given string to a date object (ISO) then format it using
    the given format (using Django's |date template filter)
    """
    try:
        d = date.fromisoformat(datestr)
    except (ValueError, TypeError):
        return ""
    return datefilter(d, dateformat)
