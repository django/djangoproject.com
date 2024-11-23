import decimal
import json
import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.forms.models import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction

from .forms import DjangoHeroForm, DonationForm, PaymentForm
from .models import DjangoHero, Donation, Payment, Testimonial

logger = logging.getLogger(__name__)


def index(request):
    testimonial = Testimonial.objects.filter(is_active=True).order_by("?").first()
    return render(
        request,
        "fundraising/index.html",
        {
            "testimonial": testimonial,
        },
    )


@require_POST
def configure_checkout_session(request):
    """
    Configure the payment session for Stripe.
    Return the Session ID.

    Key attributes are:

    - mode: payment (for one-time charge) or subscription
    - line_items: including price_data because users configure the donation
                  price.

    TODOs

    - Standard amounts could use active Prices, rather than ad-hoc price_data.
    - Tie Stripe customers to site User accounts.
      - If a user is logged in, we can create the session for the correct
        customer.
      - Stripe's documented flows are VERY keen that we create the customer
        first, although the session will do that if we don't.
    - Allow selecting currency. (Smaller task.) Users receive an additional
      charge making payments in foreign currencies. Stripe will convert all
      payments without further charge.
    """

    # Form data:
    # - The interval: which determines the Product and the mode.
    # - The amount: which goes to the Price data.
    form = PaymentForm(request.POST)
    if not form.is_valid():
        data = {"success": False, "error": form.errors}
        return JsonResponse(data)

    amount = form.cleaned_data["amount"]
    interval = form.cleaned_data["interval"]

    product_details = settings.PRODUCTS[interval]
    is_subscription = product_details.get("recurring", True)

    price_data = {
        "currency": "usd",
        "unit_amount": amount * 100,
        "product": product_details["product_id"],
    }
    if is_subscription:
        price_data["recurring"] = {
            "interval": product_details["interval"],
            "interval_count": product_details["interval_count"],
        }

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": price_data, "quantity": 1}],
            mode="subscription" if is_subscription else "payment",
            success_url=request.build_absolute_uri(reverse("fundraising:thank-you")),
            cancel_url=request.build_absolute_uri(reverse("fundraising:index")),
            # TODO: Drop this when updating API.
            stripe_version="2020-08-27",
        )

        return JsonResponse({"success": True, "sessionId": session["id"]})
    except Exception as e:
        logger.exception("Error configuring Stripe session.")
        return JsonResponse({"success": False, "error": str(e)})


def thank_you(request):
    """
    Generic thank you page. In theory only reached via successful payment, but
    no information is passed from Stripe to be sure.
    """
    return render(request, "fundraising/thank-you.html", {})


# TODO: Use Stripe's customer portal.
@never_cache
def manage_donations(request, hero):
    hero = get_object_or_404(DjangoHero, pk=hero)
    recurring_donations = hero.donation_set.exclude(stripe_subscription_id="")
    past_payments = (
        Payment.objects.filter(donation__donor=hero)
        .select_related("donation")
        .order_by("-date")
    )

    ModifyDonationsFormset = modelformset_factory(Donation, form=DonationForm, extra=0)

    if request.method == "POST":
        hero_form = DjangoHeroForm(
            data=request.POST,
            files=request.FILES,
            instance=hero,
        )
        modify_donations_formset = ModifyDonationsFormset(
            request.POST, queryset=recurring_donations
        )

        if hero_form.is_valid() and modify_donations_formset.is_valid():
            hero_form.save()
            modify_donations_formset.save()
            messages.success(request, _("Your information has been updated."))
    else:
        hero_form = DjangoHeroForm(instance=hero)
        modify_donations_formset = ModifyDonationsFormset(queryset=recurring_donations)

    return render(
        request,
        "fundraising/manage-donations.html",
        {
            "hero": hero,
            "hero_form": hero_form,
            "modify_donations_formset": modify_donations_formset,
            "recurring_donations": recurring_donations,
            "past_payments": past_payments,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        },
    )


@require_POST
def update_card(request):
    donation = get_object_or_404(Donation, id=request.POST["donation_id"])
    try:
        customer = stripe.Customer.retrieve(donation.stripe_customer_id)
        subscription = customer.subscriptions.retrieve(donation.stripe_subscription_id)
        subscription.source = request.POST["stripe_token"]
        subscription.save()
    except stripe.error.StripeError as e:
        data = {"success": False, "error": str(e)}
    else:
        data = {"success": True}
    return JsonResponse(data)


@require_POST
def cancel_donation(request, hero):
    donation_id = request.POST.get("donation")
    hero = get_object_or_404(DjangoHero, pk=hero)
    donations = hero.donation_set.exclude(stripe_subscription_id="")
    donation = get_object_or_404(donations, pk=donation_id)

    customer = stripe.Customer.retrieve(donation.stripe_customer_id)
    customer.subscriptions.retrieve(donation.stripe_subscription_id).delete()

    donation.stripe_subscription_id = ""
    donation.save()

    messages.success(request, _("Your donation has been canceled."))
    return redirect("fundraising:manage-donations", hero=hero.pk)


@require_POST
@csrf_exempt
def receive_webhook(request):
    try:
        data = json.loads(request.body.decode())
    except ValueError:
        return HttpResponse(422)

    # For security, re-request the event object from Stripe.
    # TODO: Verify shared secret here?
    try:
        event = stripe.Event.retrieve(data["id"])
    except stripe.error.InvalidRequestError:
        return HttpResponse(422)

    return WebhookHandler(event).handle()


class WebhookHandler:
    def __init__(self, event):
        self.event = event

    def handle(self):
        handlers = {
            "invoice.payment_succeeded": self.payment_succeeded,
            "invoice.payment_failed": self.payment_failed,
            "customer.subscription.deleted": self.subscription_cancelled,
            "checkout.session.completed": self.checkout_session_completed,
        }
        handler = handlers.get(self.event.type, lambda: HttpResponse(422))
        if not self.event.data.object:
            return HttpResponse(status=422)
        return handler()

    def payment_succeeded(self):
        invoice = self.event.data.object
        # Ensure we haven't already processed this payment
        if Payment.objects.filter(stripe_charge_id=invoice.charge).exists():
            # We need a 2xx response otherwise Stripe will keep trying.
            return HttpResponse()
        donation = get_object_or_404(
            Donation, stripe_subscription_id=invoice.subscription
        )
        amount = decimal.Decimal(invoice.total) / 100
        if invoice.charge:
            donation.payment_set.create(amount=amount, stripe_charge_id=invoice.charge)
        return HttpResponse(status=201)

    def subscription_cancelled(self):
        subscription = self.event.data.object
        donation = get_object_or_404(Donation, stripe_subscription_id=subscription.id)
        donation.stripe_subscription_id = ""
        donation.save()

        mail_text = render_to_string(
            "fundraising/email/subscription_cancelled.txt", {"donation": donation}
        )
        send_mail(
            _("Payment cancelled"),
            mail_text,
            settings.DEFAULT_FROM_EMAIL,
            [donation.donor.email],
        )

        return HttpResponse(status=204)

    def payment_failed(self):
        invoice = self.event.data.object
        donation = get_object_or_404(
            Donation, stripe_subscription_id=invoice.subscription
        )

        mail_text = render_to_string(
            "fundraising/email/payment_failed.txt", {"donation": donation}
        )
        send_mail(
            _("Payment failed"),
            mail_text,
            settings.DEFAULT_FROM_EMAIL,
            [donation.donor.email],
        )

        return HttpResponse(status=204)

    def get_donation_interval(self, session):
        """
        Helper to determine Donation.interval from completed Stripe Session.
        """
        if session.mode == "payment":
            return "onetime"

        # Access the interval via the attached price object.
        # See https://stripe.com/docs/api/subscriptions/object
        # TODO: remove stripe_version when updating account settings.
        subscription = stripe.Subscription.retrieve(
            session.subscription, stripe_version="2020-08-27"
        )
        recurrance = subscription["items"].data[0].price.recurring
        if recurrance.interval == "year":
            return "yearly"
        elif recurrance.interval_count == 3:
            return "quarterly"
        else:
            return "monthly"

    @transaction.atomic
    def checkout_session_completed(self):
        """
        > Occurs when a Checkout Session has been successfully completed.
        https://stripe.com/docs/api/events/types#event_types-checkout.session.completed
        
        All database operations are now wrapped in a transaction - if any operation fails,
        all changes will be rolled back to maintain data consistency.
        """
        session = self.event.data.object
        # TODO: remove stripe_version when updating account settings.
        customer = stripe.Customer.retrieve(
            session.customer, stripe_version="2020-08-27"
        )
        hero, _created = DjangoHero.objects.get_or_create(
            stripe_customer_id=customer.id,
            defaults={
                "email": customer.email,
            },
        )
        interval = self.get_donation_interval(session)
        dollar_amount = decimal.Decimal(session.amount_total / 100).quantize(
            decimal.Decimal(".01"), rounding=decimal.ROUND_HALF_UP
        )
        donation = Donation.objects.create(
            donor=hero,
            stripe_customer_id=customer.id,
            receipt_email=customer.email,
            subscription_amount=dollar_amount,
            interval=interval,
            stripe_subscription_id=session.subscription or "",
        )
        if interval == "onetime":
            payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
            charge = payment_intent.charges.data[0]
            donation.payment_set.create(
                amount=dollar_amount,
                stripe_charge_id=charge.id,
            )

        # Send an email message about managing your donation
        message = render_to_string(
            "fundraising/email/thank-you.html", {"donation": donation}
        )
        send_mail(
            _("Thank you for your donation to the Django Software Foundation"),
            message,
            settings.FUNDRAISING_DEFAULT_FROM_EMAIL,
            [donation.receipt_email],
        )

        return HttpResponse(status=204)