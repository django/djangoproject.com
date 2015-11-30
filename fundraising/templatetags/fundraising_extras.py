from decimal import Decimal

from django import template
from django.conf import settings
from django.db import models
from django.template.defaultfilters import floatformat

from fundraising.forms import DonateForm, RecurringDonateForm
from fundraising.models import DEFAULT_DONATION_AMOUNT, DjangoHero, Donation

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
        'display_logo_amount': context['display_logo_amount'],
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'user': context['user'],
    }


@register.inclusion_tag('fundraising/includes/recurring_donation_form.html', takes_context=True)
def recurring_donation_form(context):
    donated_amount = Donation.objects.filter(campaign__isnull=True).aggregate(models.Sum('payment__amount'))
    total_donors = Donation.objects.filter(campaign__isnull=True).count()
    form = RecurringDonateForm(initial={
        'amount': DEFAULT_DONATION_AMOUNT,
    })

    return {
        'donated_amount': donated_amount['payment__amount__sum'] or 0,
        'total_donors': total_donors,
        'form': form,
        'display_logo_amount': context['display_logo_amount'],
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'user': context['user'],
    }


@register.inclusion_tag('fundraising/includes/display_django_heros.html', takes_context=True)
def display_django_heros(context, campaign):
    individuals = DjangoHero.objects.for_campaign(campaign, hero_type='individual')
    organizations = DjangoHero.objects.for_campaign(campaign, hero_type='organization')
    return {
        'display_logo_amount': context['display_logo_amount'],
        'individuals': individuals,
        'organizations': organizations,
    }


@register.inclusion_tag('fundraising/includes/display_django_heros.html', takes_context=True)
def display_recurring_django_heros(context):
    individuals = DjangoHero.objects.for_campaign(None, hero_type='individual')
    organizations = DjangoHero.objects.for_campaign(None, hero_type='organization')
    return {
        'display_logo_amount': context['display_logo_amount'],
        'individuals': individuals,
        'organizations': organizations,
    }
