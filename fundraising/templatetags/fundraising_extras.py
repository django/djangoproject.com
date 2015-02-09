from decimal import Decimal

from django import template
from django.db import models
from django.template.defaultfilters import floatformat

from fundraising.models import (
    DjangoHero, Donation, DISPLAY_LOGO_AMOUNT, DEFAULT_DONATION_AMOUNT,
)
from fundraising.forms import DonateForm

register = template.Library()


@register.filter
def as_percentage(part, total):
    if total is None or part is None:
        return "0.00"

    try:
        return floatformat((part / total) * Decimal("100.0"))
    except ZeroDivisionError:
        return "0.00"


@register.inclusion_tag('fundraising/includes/donation_snippet.html')
def donation_snippet():
    try:
        donation = DjangoHero.objects.filter(approved=True, is_visible=True).order_by('?')[:1]
        donation = donation.annotate(donated_amount=models.Sum('donation__amount')).get()
    except DjangoHero.DoesNotExist:
        donation = None

    return {'donation': donation}


@register.inclusion_tag('fundraising/includes/donation_form_with_heart.html')
def donation_form_with_heart(campaign):
    donated_amount = Donation.objects.filter(campaign=campaign).aggregate(models.Sum('amount'))
    total_donors = DjangoHero.objects.filter(donation__campaign=campaign).count()
    form = DonateForm(initial={
        'amount': DEFAULT_DONATION_AMOUNT
    })

    return {
        'campaign': campaign,
        'donated_amount': donated_amount['amount__sum'] or 0,
        'total_donors': total_donors,
        'form': form,
        'display_logo_amount': DISPLAY_LOGO_AMOUNT,
    }
