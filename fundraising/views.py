import json
import stripe
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.forms.models import modelformset_factory
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .exceptions import DonationError
from .forms import DjangoHeroForm, PaymentForm, DonationForm
from .models import Campaign, DjangoHero, Donation, Payment, Testimonial


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
                'error': str(donation_error),
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
        form = DjangoHeroForm(
            data=request.POST,
            files=request.FILES,
            instance=donation.donor,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! You're a Hero.")
            return redirect(
                **{'to': 'fundraising:campaign', 'slug': donation.campaign.slug}
                if donation.campaign else {'to': 'fundraising:index'}
            )
    else:
        form = DjangoHeroForm(instance=donation.donor)

    return render(request, 'fundraising/thank-you.html', {
        'donation': donation,
        'form': form,
    })


def manage_donations(request, hero):
    hero = get_object_or_404(DjangoHero, pk=hero)
    recurring_donations = hero.donation_set.filter(
        stripe_subscription_id__isnull=False
    ).exclude(
        stripe_subscription_id=''
    )

    ModifyDonationsFormset = modelformset_factory(Donation, form=DonationForm, extra=0)

    if request.method == 'POST':
        hero_form = DjangoHeroForm(
            data=request.POST,
            files=request.FILES,
            instance=hero,
        )
        modify_donations_formset = ModifyDonationsFormset(
            request.POST,
            queryset=recurring_donations
        )

        if hero_form.is_valid() and modify_donations_formset.is_valid():
            hero_form.save()
            modify_donations_formset.save()
            messages.success(request, "Your information has been updated.")
    else:
        hero_form = DjangoHeroForm(instance=hero)
        modify_donations_formset = ModifyDonationsFormset(
            queryset=recurring_donations
        )

    return render(request, 'fundraising/manage-donations.html', {
        'hero': hero,
        'hero_form': hero_form,
        'modify_donations_formset': modify_donations_formset,
        'recurring_donations': recurring_donations,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })


@require_POST
def update_card(request):
    donation = get_object_or_404(Donation, id=request.POST['donation_id'])
    try:
        customer = stripe.Customer.retrieve(donation.stripe_customer_id)
        subscription = customer.subscriptions.retrieve(donation.stripe_subscription_id)
        subscription.source = request.POST['stripe_token']
        subscription.save()
    except stripe.StripeError as e:
        data = {'success': False, 'error': str(e)}
    else:
        data = {'success': True}
    return JsonResponse(data)


def cancel_donation(request, hero, donation):
    hero = get_object_or_404(DjangoHero, pk=hero)
    donation = get_object_or_404(Donation, pk=donation, donor=hero,
        stripe_subscription_id__isnull=False)

    customer = stripe.Customer.retrieve(donation.stripe_customer_id)
    customer.subscriptions.retrieve(donation.stripe_subscription_id).delete()

    donation.stripe_subscription_id = None
    donation.save()

    return redirect('fundraising:manage-donations', hero=hero.pk)


@require_POST
@csrf_exempt
def receive_webhook(request):
    data = json.loads(request.body.decode())
    event = stripe.resource.convert_to_stripe_object(data, stripe.api_key)

    return WebhookHandler(event).handle()


class WebhookHandler(object):
    def __init__(self, event):
        self.event = event

    def handle(self):
        handlers = {
            'invoice.payment_succeeded': self.payment_succeeded,
            'invoice.payment_failed': self.payment_failed,
            'customer.subscription.deleted': self.subscription_cancelled,
        }
        handler = handlers.get(self.event.type, lambda: HttpResponse(404))
        return handler()

    def payment_succeeded(self):
        invoice = self.event.data.object
        # Ensure we haven't already processed this payment
        if Payment.objects.filter(stripe_charge_id=invoice.charge).exists():
            # We need a 2xx response otherwise Stripe will keep trying.
            return HttpResponse()
        donation = get_object_or_404(
            Donation, stripe_subscription_id=invoice.subscription)
        Payment.objects.create(
            donation=donation, amount=invoice.total, stripe_charge_id=invoice.charge)
        return HttpResponse(status=201)

    def subscription_cancelled(self):
        subscription = self.event.data.object
        donation = get_object_or_404(
            Donation, stripe_subscription_id=subscription.id)
        donation.stripe_subscription_id = ''
        donation.save()

        mail_text = render_to_string(
            'fundraising/email/subscription_cancelled.txt', {'donation': donation})
        send_mail('Payment cancelled', mail_text,
            settings.DEFAULT_FROM_EMAIL, [donation.donor.email])

        return HttpResponse(status=204)

    def payment_failed(self):
        invoice = self.event.data.object
        donation = get_object_or_404(
            Donation, stripe_subscription_id=invoice.subscription)

        mail_text = render_to_string(
            'fundraising/email/payment_failed.txt', {'donation': donation})
        send_mail('Payment failed', mail_text,
            settings.DEFAULT_FROM_EMAIL, [donation.donor.email])

        return HttpResponse(status=204)

