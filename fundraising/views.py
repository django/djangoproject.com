from datetime import date
from decimal import Decimal, DecimalException

from django.conf import settings
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import redirect, render, get_object_or_404

import stripe

from .forms import DonateForm, PaymentForm, DjangoHeroForm
from .models import (
    DjangoHero, Donation, Testimonial, RESTART_GOAL, DEFAULT_DONATION_AMOUNT,
    DISPLAY_LOGO_AMOUNT, WEEKLY_GOAL,
)


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

    return render(request, 'fundraising/index.html', {
        'donated_amount': donated_amount['amount__sum'] or 0,
        'goal_amount': RESTART_GOAL,
        'donors_with_logo': donors_with_logo,
        'other_donors': other_donors,
        'total_donors': DjangoHero.objects.count(),
        'form': DonateForm(initial={'amount': DEFAULT_DONATION_AMOUNT}),
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
            # Create the charge on Stripe's servers - this will charge the user's card
            try:
                amount = form.cleaned_data['amount']
                token = form.cleaned_data['stripe_token']
                # First create a Stripe customer so that we can store
                # people's email address on that object later
                customer = stripe.Customer.create(card=token)
                # Charge the customer's credit card on Stripe's servers;
                # the amount is in cents!
                charge = stripe.Charge.create(
                    amount=int(amount * 100),
                    currency='usd',
                    customer=customer.id,
                )
            except (stripe.StripeError, ValueError):
                # The card has been declined, we want to see what happened
                # in Sentry
                raise
            else:
                donation = Donation.objects.create(
                    amount=amount,
                    stripe_charge_id=charge.id,
                    stripe_customer_id=customer.id,
                )
                return redirect(donation)
        else:
            if 'amount' in form.errors:
                show_amount = True
    else:
        fixed_amount = request.GET.get('amount') or None
        initial = {}
        if fixed_amount:
            try:
                initial = {'amount': Decimal(fixed_amount)}
            except DecimalException:
                show_amount = True
        form = PaymentForm(initial=initial, fixed_amount=fixed_amount)

    if show_amount:
        form.show_amount()

    context = {
        'form': form,
        'fixed_amount': fixed_amount,
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
                customer.email = hero.email
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
