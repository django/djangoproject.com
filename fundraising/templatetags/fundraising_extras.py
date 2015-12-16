from decimal import Decimal

from django import template
from django.conf import settings
from django.db import models
from django.template.defaultfilters import floatformat

from fundraising.forms import DonateForm
from fundraising.models import (
    DEFAULT_DONATION_AMOUNT, DISPLAY_DONOR_DAYS, GOAL_AMOUNT, GOAL_START_DATE,
    LEADERSHIP_LEVEL_AMOUNT, DjangoHero, Payment,
)
from members.models import CorporateMember

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
        donation = DjangoHero.objects.filter(
            approved=True,
            is_visible=True,
        ).exclude(name='').order_by('?')[:1].get()
    except DjangoHero.DoesNotExist:
        donation = None

    return {'donation': donation}


@register.inclusion_tag('fundraising/includes/donation_form_with_heart.html', takes_context=True)
def donation_form_with_heart(context):
    user = context['user']
    donated_amount = Payment.objects.filter(date__gte=GOAL_START_DATE).aggregate(models.Sum('amount'))
    total_donors = DjangoHero.objects.filter(donation__payment__date__gte=GOAL_START_DATE).distinct().count()
    form = DonateForm(initial={
        'amount': DEFAULT_DONATION_AMOUNT,
    })

    return {
        'goal_amount': GOAL_AMOUNT,
        'donated_amount': donated_amount['amount__sum'] or 0,
        'total_donors': total_donors,
        'form': form,
        'display_logo_amount': LEADERSHIP_LEVEL_AMOUNT,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'user': user,
    }


@register.inclusion_tag('fundraising/includes/display_django_heros.html')
def display_django_heros():
    donors = DjangoHero.objects.for_public_display()
    i = 0
    for i, donor in enumerate(donors):
        if donor.donated_amount is not None and donor.donated_amount < LEADERSHIP_LEVEL_AMOUNT:
            break
    return {
        'silver_members': CorporateMember.objects.for_public_display(),
        'leaders': donors[:i],
        'heros': donors[i:],
        'display_donor_days': DISPLAY_DONOR_DAYS,
        'display_logo_amount': LEADERSHIP_LEVEL_AMOUNT,
    }
