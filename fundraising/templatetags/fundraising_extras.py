from decimal import Decimal

from django import template
from django.db import models
from django.template.defaultfilters import floatformat

from fundraising.models import DjangoHero

register = template.Library()


@register.filter
def as_percentage(part, total):
    if total is None or part is None:
        return "0.00"

    try:
        return floatformat((part / total) * Decimal("100.0"))
    except ZeroDivisionError:
        return "0.00"


@register.inclusion_tag('fundraising/donation_snippet.html')
def donation_snippet():
    try:
        donation = DjangoHero.objects.filter(is_visible=True).order_by('?')[:1]
        donation = donation.annotate(donated_amount=models.Sum('donation__amount')).get()
    except DjangoHero.DoesNotExist:
        donation = None

    return {'donation': donation}
