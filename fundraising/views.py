from datetime import date
from decimal import Decimal, DecimalException

from django.conf import settings
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import redirect, render, get_object_or_404

import stripe

from .exceptions import DonationError
from .forms import DonateForm, PaymentForm, DjangoHeroForm
from .models import (
    DjangoHero, Donation, Testimonial, RESTART_GOAL, DEFAULT_DONATION_AMOUNT,
    DISPLAY_LOGO_AMOUNT, WEEKLY_GOAL, STRETCH_GOAL,
)
from .utils import shuffle_donations


def index(request):
    # replace with get_week_begin_end_datetimes() if we switch to a weekly
    # goal at some point
    begin = date(2015, 1, 1)
    end = date(2016, 1, 1)
    donated_amount = Donation.objects.filter(
        created__gte=begin, created__lt=end,
    ).aggregate(Sum('amount'))

    donors_with_logo = DjangoHero.objects.in_period(begin, end, with_logo=True)
    other_donors = DjangoHero.objects.in_period(begin, end)

    campaign = request.GET.get('campaign')

    return render(request, 'fundraising/index.html', {
        'donated_amount': donated_amount['amount__sum'] or 0,
        'goal_amount': RESTART_GOAL,
        'stretch_goal_amount': STRETCH_GOAL,
        'donors_with_logo': shuffle_donations(donors_with_logo),
        'other_donors': shuffle_donations(other_donors),
        'total_donors': DjangoHero.objects.count(),
        'form': DonateForm(initial={
            'amount': DEFAULT_DONATION_AMOUNT,
            'campaign': campaign
        }),
        'testimonial': Testimonial.objects.filter(is_active=True).order_by('?').first(),
        'display_logo_amount': DISPLAY_LOGO_AMOUNT,
        'weekly_goal': WEEKLY_GOAL,
    })


def donate(request):
    show_amount = False
    if request.method == 'POST':
        fixed_amount = None
        form = PaymentForm(request.POST)

        if form.is_valid():
            # Try to create the charge on Stripe's servers - this will charge the user's card
            try:
                donation = form.make_donation()
            except DonationError as donation_error:
                # If a failure happened show the error but populate the
                # form again with those values that can be reused
                # Note: no stripe_token added to initials here
                initial = {
                    'amount': form.cleaned_data['amount'],
                    'receipt_email': form.cleaned_data['receipt_email'],
                    'campaign': form.cleaned_data['campaign'],
                }
                context = {
                    'form': PaymentForm(initial=initial),
                    'donation_error': str(donation_error),
                    'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
                }
                return render(request, 'fundraising/donate.html', context)
            else:
                return redirect(donation)
        else:
            if 'amount' in form.errors:
                show_amount = True
    else:
        fixed_amount = request.GET.get('amount') or None
        campaign = request.GET.get('campaign')
        initial = {'campaign': campaign}
        if fixed_amount:
            try:
                initial['amount'] = Decimal(fixed_amount)
            except DecimalException:
                show_amount = True
        form = PaymentForm(initial=initial, fixed_amount=fixed_amount)

    if show_amount:
        form.show_amount()

    context = {
        'form': form,
        'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'fundraising/donate.html', context)


def thank_you(request, donation):
    donation = get_object_or_404(Donation, pk=donation)
    if request.method == 'POST':
        if donation.donor:
            form = DjangoHeroForm(
                data=request.POST,
                files=request.FILES,
                instance=donation.donor,
            )
        else:
            form = DjangoHeroForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            hero = form.save()
            try:
                customer = stripe.Customer.retrieve(donation.stripe_customer_id)
                customer.description = hero.name or None
                customer.email = hero.email or None
                customer.save()
            except stripe.StripeError:
                raise
            else:
                donation.donor = hero
                donation.save()
                messages.success(request, "Thank you! You're a Hero.")
                return redirect('fundraising:index')
    else:
        if donation.donor:
            form = DjangoHeroForm(instance=donation.donor)
        else:
            form = DjangoHeroForm()

    return render(request, 'fundraising/thank-you.html', {
        'donation': donation,
        'form': form,
    })
