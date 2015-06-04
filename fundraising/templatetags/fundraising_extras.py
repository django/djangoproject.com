from decimal import Decimal

from django import template
from django.conf import settings
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
        donation = donation.annotate(donated_amount=models.Sum('donation__payment__amount')).get()
    except DjangoHero.DoesNotExist:
        donation = None

    return {'donation': donation}


@register.inclusion_tag('fundraising/includes/donation_form_with_heart.html', takes_context=True)
def donation_form_with_heart(context, campaign):
    user = context['user']
    donated_amount = Donation.objects.filter(campaign=campaign).aggregate(models.Sum('payment__amount'))
    total_donors = DjangoHero.objects.filter(donation__campaign=campaign).count()
    form = DonateForm(initial={
        'amount': DEFAULT_DONATION_AMOUNT,
        'campaign': campaign,
    })

    return {
        'campaign': campaign,
        'donated_amount': donated_amount['payment__amount__sum'] or 0,
        'total_donors': total_donors,
        'form': form,
        'display_logo_amount': DISPLAY_LOGO_AMOUNT,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'user': user,
    }


@register.inclusion_tag('fundraising/includes/display_django_heros.html')
def display_django_heros(campaign):
    individuals = DjangoHero.objects.for_campaign(campaign, hero_type='individual')
    organizations = DjangoHero.objects.for_campaign(campaign, hero_type='organization')
    return {
        'individuals': individuals,
        'organizations': organizations,
    }
