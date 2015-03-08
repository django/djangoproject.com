from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

import stripe

from .exceptions import DonationError
from .forms import PaymentForm, DjangoHeroForm
from .models import Donation, Testimonial, Campaign


def index(request):
    campaigns = Campaign.objects.filter(is_public=True, is_active=True)
    if len(campaigns) == 1:
        return redirect('fundraising:campaign', slug=campaigns[0].slug)

    return render(request, 'fundraising/index.html', {
        'campaigns': campaigns,
    })


def campaign(request, slug):
    filter_params = {} if request.user.is_staff else {'is_public': True}
    campaign = get_object_or_404(Campaign, slug=slug, **filter_params)
    testimonial = Testimonial.objects.filter(campaign=campaign, is_active=True).order_by('?').first()

    return render(request, campaign.template, {
        'campaign': campaign,
        'testimonial': testimonial,
    })


@require_POST
def donate(request):
    form = PaymentForm(request.POST)

    if form.is_valid():
        # Try to create the charge on Stripe's servers - this will charge the user's card
        try:
            donation = form.make_donation()
        except DonationError as donation_error:
            data = {
                'success': False,
                'error': donation_error.message,
            }
        else:
            data = {
                'success': True,
                'redirect': donation.get_absolute_url(),
            }
    else:
        data = {
            'success': False,
            'error': form.errors.as_json(),
        }
    return JsonResponse(data)


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
                return redirect(**{'to': 'fundraising:campaign', 'slug': donation.campaign.slug}
                    if donation.campaign else {'to': 'fundraising:index'})
    else:
        if donation.donor:
            form = DjangoHeroForm(instance=donation.donor)
        else:
            form = DjangoHeroForm()

    return render(request, 'fundraising/thank-you.html', {
        'donation': donation,
        'form': form,
    })
