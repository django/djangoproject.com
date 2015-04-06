from decimal import Decimal
import stripe

from django import forms
from django.utils.safestring import mark_safe

from .exceptions import DonationError
from .models import DjangoHero, Donation


class DjangoHeroForm(forms.ModelForm):
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'required',
                'placeholder': 'Your name or the name of your organization',
            },
        )
    )
    url = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'To which URL should we link your name to?',
            },
        )
    )
    logo = forms.FileField(
        required=False,
        help_text=(
            "If you've donated at least US $200, you can submit your logo and "
            "we will display it, too."
        ),
    )
    email = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'required',
                'placeholder': 'Contact email address',
                'type': 'email',
            },
        ),
        help_text=(
            'We ask for your email address here only to contact you about '
            'future fundraising campaigns if you give us your permission below.'
        ),
    )
    is_visible = forms.BooleanField(
        required=False,
        label=(
            "Yes, display my name, URL, and logo on this site. "
            "It'll be displayed shortly after we verify it."
        ),
    )
    is_subscribed = forms.BooleanField(
        required=False,
        label=(
            'Yes, the Django Software Foundation can inform me about '
            'future fundraising campaigns by email.'
        ),
    )
    is_amount_displayed = forms.BooleanField(
        required=False,
        label='Yes, display the amount of my donation.'
    )

    class Meta:
        model = DjangoHero
        fields = (
            'name', 'url', 'logo', 'is_visible',
            'is_amount_displayed', 'email', 'is_subscribed',
        )

    def __init__(self, *args, **kwargs):
        super(DjangoHeroForm, self).__init__(*args, **kwargs)
        self.checkbox_fields = [
            name for name, field in self.fields.items()
            if isinstance(field.widget, forms.CheckboxInput)
        ]


class StripeTextInput(forms.TextInput):
    """
    Inspired by widgets in django-zebra
    """
    def _add_data_stripe_attr(self, name, kwargs):
        kwargs.setdefault('attrs', {}).update({'data-stripe': name})
        return kwargs

    def _strip_name_attr(self, widget_string, name):
        return widget_string.replace("name=\"%s\"" % (name,), "")

    def render(self, name, *args, **kwargs):
        kwargs = self._add_data_stripe_attr(name, kwargs)
        rendered = super(StripeTextInput, self).render(name, *args, **kwargs)
        return mark_safe(self._strip_name_attr(rendered, name))


class DonateForm(forms.Form):
    AMOUNT_CHOICES = (
        ('5.00', 'US $5'),
        ('25.00', 'US $25'),
        ('50.00', '1 hour: US $50'),
        ('100.00', '2 hours: US $100'),
        ('200.00', '4 hours: US $200'),
        ('400.00', '1 day: US $400'),
        ('1200.00', '3 days: US $1,200'),
        ('2800.00', '1 week: US $2,800'),
        ('custom', 'Other amount'),
    )
    AMOUNT_VALUES = dict(AMOUNT_CHOICES).keys()

    amount = forms.ChoiceField(choices=AMOUNT_CHOICES)
    campaign = forms.CharField(required=False, widget=forms.HiddenInput())


class PaymentForm(forms.Form):
    AMOUNT_PLACEHOLDER = 'Amount in US Dollar'
    amount = forms.DecimalField(
        required=True,
        decimal_places=2,
        max_digits=9,
        min_value=Decimal('0.50'),  # Minimum payment from Stripe API
        widget=forms.TextInput(
            attrs={
                'class': 'required',
                'placeholder': AMOUNT_PLACEHOLDER,
                'tabindex': 1,
            },
        ),
        help_text='Please enter the amount of your donation in US Dollar',
    )
    number = forms.CharField(
        required=False,
        max_length=20,
        widget=StripeTextInput(
            attrs={
                'placeholder': 'Card number',
                'size': 20,
                'pattern': '\d*',  # number input on mobile
                'autocomplete': 'cc-number',  # for autofill spec
                'tabindex': 2,
            },
        ),
    )
    cvc = forms.CharField(
        required=False,
        widget=StripeTextInput(
            attrs={
                'placeholder': 'CVC - Card Verification Code',
                'size': 4,
                'pattern': '\d*',  # number input on mobile
                'autocomplete': 'off',
                'tabindex': 3,
            },
        ),
    )
    expires = forms.CharField(
        required=False,
        widget=StripeTextInput(
            attrs={
                'placeholder': 'Expires MM/YYYY',
                'pattern': '\d*',  # number input on mobile
                'autocomplete': 'cc-exp',
                'tabindex': 4,
            },
        ),
    )
    receipt_email = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'required',
                'placeholder': 'Receipt email address (optional)',
                'type': 'email',
                'tabindex': 5,
            },
        ),
        help_text=(
            'We ask for your email address here to be able to send you a '
            'receipt. Leave empty if you do not want one.'
        ),
    )
    # added to the form if given as a GET parameter
    campaign = forms.CharField(required=False, widget=forms.HiddenInput())
    # added by the donation form JavaScript via Stripe.js
    stripe_token = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, data=None, fixed_amount=None, *args, **kwargs):
        super(PaymentForm, self).__init__(data, *args, **kwargs)
        self.fixed_amount = fixed_amount
        if fixed_amount is not None or (data and 'amount' in data):
            self.hide_amount()

    def hide_amount(self):
        self.fields['amount'].widget = forms.HiddenInput()

    def show_amount(self):
        self.fields['amount'].widget = forms.TextInput(
            attrs={
                'class': 'required',
                'placeholder': self.AMOUNT_PLACEHOLDER,
            },
        )

    def make_donation(self):
        receipt_email = self.cleaned_data.get('receipt_email')
        amount = self.cleaned_data['amount']
        campaign = self.cleaned_data['campaign']
        stripe_token = self.cleaned_data['stripe_token']

        try:
            # First create a Stripe customer so that we can store
            # people's email address on that object later
            customer = stripe.Customer.create(card=stripe_token)
            # Charge the customer's credit card on Stripe's servers;
            # the amount is in cents!
            charge = stripe.Charge.create(
                amount=int(amount * 100),
                currency='usd',
                customer=customer.id,
                receipt_email=receipt_email or None,  # set to None if given an empty string
            )
        except stripe.error.CardError as card_error:
            raise DonationError(
                "We're sorry but we had problems charging your card. "
                'Here is what Stripe replied: "%s"' % str(card_error))

        except stripe.error.InvalidRequestError:
            # Invalid parameters were supplied to Stripe's API
            raise DonationError(
                "We're sorry but something went wrong while processing "
                "your card details. No charge was done. Please try "
                "again or get in touch with us.")

        except stripe.error.APIConnectionError:
            # Network communication with Stripe failed
            raise DonationError(
                "We're sorry but we have technical difficulties "
                "reaching our payment processor Stripe. No charge "
                "was done. Please try again later.")

        except stripe.error.AuthenticationError:
            # Authentication with Stripe's API failed
            raise

        except (stripe.StripeError, Exception):
            # The card has been declined, we want to see what happened
            # in Sentry
            raise

        else:
            # Finally create the donation and return it
            donation = Donation.objects.create(
                amount=amount,
                stripe_charge_id=charge.id,
                stripe_customer_id=customer.id,
                campaign_name=campaign,
                receipt_email=receipt_email,
            )
            return donation
