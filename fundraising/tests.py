import os
from datetime import date, timedelta
from functools import partial
from operator import attrgetter
from unittest.mock import patch

import stripe

from PIL import Image
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from .exceptions import DonationError
from .forms import PaymentForm
from .models import DjangoHero, Donation
from .utils import shuffle_donations


def _fake_random(*results):
    """
    Return a callable that generates the given results when called.
    Useful for mocking random.random().

    Example:

    >>> r = _fake_random(1, 2, 3)
    >>> r()
    1
    >>> r()
    2
    >>> r()
    3
    """
    return partial(next, iter(results))


class TestIndex(TestCase):
    def test_donors_count(self):
        DjangoHero.objects.create()
        response = self.client.get(reverse('fundraising:index'))
        self.assertEqual(response.context['total_donors'], 1)

    def test_anonymous_donor(self):
        hero = DjangoHero.objects.create(is_visible=True, approved=True)
        Donation.objects.create(donor=hero, amount='5')
        response = self.client.get(reverse('fundraising:index'))
        self.assertContains(response, 'Anonymous Hero')

    def test_anonymous_donor_with_logo(self):
        hero = DjangoHero.objects.create(is_visible=True, approved=True, logo='yes')  # We don't need an actual image
        Donation.objects.create(donor=hero, amount='5')
        response = self.client.get(reverse('fundraising:index'))
        self.assertContains(response, 'Anonymous Hero')

    def test_hide_campaign_input(self):
        # Checking if rendered output contains campaign form field
        # to not generate ugly URLs
        response = self.client.get(reverse('fundraising:index'))
        self.assertNotContains(response, 'name="campaign"')

        response = self.client.get(reverse('fundraising:index'), {'campaign': 'test'})
        self.assertContains(response, 'name="campaign"')

    def test_render_donate_form_with_amount(self):
        response = self.client.get(reverse('fundraising:donate'), {'amount': 50})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].fixed_amount, '50')
        self.assertEqual(response.context['publishable_key'], settings.STRIPE_PUBLISHABLE_KEY)

        # Checking if amount field is hidden
        self.assertIsInstance(response.context['form'].fields['amount'].widget, forms.HiddenInput)

        # Checking if campaign field is empty
        self.assertEqual(response.context['form'].initial['campaign'], None)

    def test_render_donate_form_without_amount(self):
        response = self.client.get(reverse('fundraising:donate'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].fixed_amount, None)
        self.assertEqual(response.context['publishable_key'], settings.STRIPE_PUBLISHABLE_KEY)

        # Checking if amount field is visible
        self.assertIsInstance(response.context['form'].fields['amount'].widget, forms.TextInput)
        # Checking if campaign field is empty
        self.assertEqual(response.context['form'].initial['campaign'], None)

    def test_render_donate_form_with_bad_amount(self):
        # this will trigger a DecimalException exception because the amount can't be
        # converted to a Decimal
        response = self.client.get(reverse('fundraising:donate'), {'amount': 'superbad'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].fixed_amount, 'superbad')
        self.assertEqual(response.context['publishable_key'], settings.STRIPE_PUBLISHABLE_KEY)

        # Checking if amount field is visible
        self.assertIsInstance(response.context['form'].fields['amount'].widget, forms.TextInput)
        # Checking if campaign field is empty
        self.assertEqual(response.context['form'].initial['campaign'], None)

    def test_render_donate_form_with_campaign(self):
        campaigns = ['sample', '']
        for campaign in campaigns:
            response = self.client.get(reverse('fundraising:donate'), {'amount': 100, 'campaign': campaign})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['form'].fixed_amount, '100')
            self.assertEqual(response.context['publishable_key'], settings.STRIPE_PUBLISHABLE_KEY)

            # Checking if amount field is hidden
            self.assertIsInstance(response.context['form'].fields['amount'].widget, forms.HiddenInput)
            # Checking if campaign field is same as campaign
            self.assertEqual(response.context['form'].initial['campaign'], campaign)

    def test_submitting_donation_form_missing_token(self):
        url = reverse('fundraising:donate')
        response = self.client.post(url, {'amount': 100})
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'fundraising/donate.html')

    def test_submitting_donation_form_invalid_amount(self):
        url = reverse('fundraising:donate')
        response = self.client.post(url, {
            'amount': 'superbad',
            'stripe_token': 'test',
        })
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(200, response.status_code)
        # Checking if amount field is visible
        self.assertIsInstance(response.context['form'].fields['amount'].widget, forms.TextInput)

    @patch('stripe.Customer.create')
    @patch('stripe.Charge.create')
    def test_submitting_donation_form(self, charge_create, customer_create):
        response = self.client.post(reverse('fundraising:donate'), {'amount': 100})
        self.assertFalse(response.context['form'].is_valid())

        response = self.client.post(reverse('fundraising:donate'), {
            'amount': 100,
            'stripe_token': 'test',
            'receipt_email': 'test@example.com',
        })
        donations = Donation.objects.all()
        self.assertEqual(donations.count(), 1)
        self.assertEqual(donations[0].amount, 100)
        self.assertEqual(donations[0].campaign_name, '')
        self.assertEqual(donations[0].receipt_email, 'test@example.com')

    @patch('stripe.Customer.create')
    @patch('stripe.Charge.create')
    def test_submitting_donation_form_with_campaign(self, charge_create, customer_create):
        response = self.client.post(reverse('fundraising:donate'), {
            'amount': 100,
            'campaign': 'test',
        })
        self.assertFalse(response.context['form'].is_valid())
        response = self.client.post(reverse('fundraising:donate'), {
            'amount': 100,
            'campaign': 'test',
            'stripe_token': 'test',
        })
        donations = Donation.objects.all()
        self.assertEqual(donations.count(), 1)
        self.assertEqual(donations[0].amount, 100)
        self.assertEqual(donations[0].campaign_name, 'test')

    @patch('stripe.Customer.create')
    @patch('stripe.Charge.create')
    def test_submitting_donation_form_error_handling(self, charge_create, customer_create):
        data = {
            'amount': 100,
            'campaign': None,
            'stripe_token': 'xxxx',
        }
        form = PaymentForm(data=data)

        self.assertTrue(form.is_valid())

        # some errors are shows as user facting DonationErrors to the user
        # some are bubbling up to raise a 500 to trigger Sentry reports
        errors = [
            [stripe.error.CardError, DonationError],
            [stripe.error.InvalidRequestError, DonationError],
            [stripe.error.APIConnectionError, DonationError],
            [stripe.error.AuthenticationError, None],
            [stripe.error.StripeError, None],
            [ValueError, None],
        ]

        for backend_exception, user_exception in errors:
            customer_create.side_effect = backend_exception('message', 'param', 'code')

            if user_exception is None:
                self.assertRaises(backend_exception, form.make_donation)
            else:
                response = self.client.post(reverse('fundraising:donate'), data)
                self.assertTrue('donation_error' in response.context)

    @patch('fundraising.forms.PaymentForm.make_donation')
    def test_submitting_donation_form_valid(self, make_donation):
        amount = 100
        donation = Donation.objects.create(
            amount=amount,
            stripe_charge_id='xxxx',
            stripe_customer_id='xxxx',
        )
        make_donation.return_value = donation
        response = self.client.post(reverse('fundraising:donate'), {
            'amount': amount,
            'campaign': None,
            'stripe_token': 'xxxx',
        })
        self.assertRedirects(response, donation.get_absolute_url())


class TestDjangoHero(TestCase):
    def setUp(self):
        kwargs = {
            'approved': True,
            'is_visible': True,
            'is_amount_displayed': True,
        }
        self.h1 = DjangoHero.objects.create(**kwargs)
        Donation.objects.create(donor=self.h1, amount='5')
        self.h2 = DjangoHero.objects.create(**kwargs)
        Donation.objects.create(donor=self.h2, amount='15')
        # hidden donation amount should display last
        kwargs['is_amount_displayed'] = False
        self.h3 = DjangoHero.objects.create(**kwargs)
        Donation.objects.create(donor=self.h3, amount='10')
        self.today = date.today()

    def test_donation_shuffling(self):
        queryset = DjangoHero.objects.in_period(self.today, self.today + timedelta(days=1))

        for random, expected in [
            (lambda: 1, [15, 10, 5]),
            (lambda: -1, [5, 10, 15]),
            (_fake_random(1, 0, 1), [15, 5, 10]),
        ]:
            with patch('fundraising.utils.random', side_effect=random):
                self.assertQuerysetEqual(
                    shuffle_donations(queryset),
                    expected,
                    attrgetter('donated_amount')
                )

    def test_thumbnail(self):
        try:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'fundraising/logos/'))
        except OSError:  # directory may already exist
            pass
        image_path = os.path.join(settings.MEDIA_ROOT, 'fundraising/logos/test_logo.jpg')
        image = Image.new('L', (500, 500))
        image.save(image_path)
        self.h1.logo = image_path
        self.h1.save()
        thumbnail = self.h1.thumbnail
        self.assertEqual(thumbnail.x, 170)
        self.assertEqual(thumbnail.y, 170)
        os.remove(image_path)
        self.assertTrue(
            os.path.exists(
                thumbnail.url.replace(settings.MEDIA_URL, '{}/'.format(settings.MEDIA_ROOT))
            )
        )

    def test_thumbnail_no_logo(self):
        self.assertIsNone(self.h2.thumbnail)

    def test_name_with_fallback(self):
        hero = DjangoHero()
        self.assertEqual(hero.name_with_fallback, 'Anonymous Hero')
        hero.name = 'Batistek'
        self.assertEqual(hero.name_with_fallback, 'Batistek')


class TestPaymentForm(TestCase):
    @patch('stripe.Customer.create')
    @patch('stripe.Charge.create')
    def test_make_donation(self, charge_create, customer_create):
        customer_create.return_value.id = 'xxxx'
        charge_create.return_value.id = 'xxxx'
        form = PaymentForm(data={
            'amount': 100,
            'campaign': None,
            'stripe_token': 'xxxx',
        })
        self.assertTrue(form.is_valid())
        donation = form.make_donation()
        self.assertEqual(100, donation.amount)

    @patch('stripe.Customer.create')
    @patch('stripe.Charge.create')
    def test_make_donation_exception(self, charge_create, customer_create):
        customer_create.side_effect = ValueError("Something is wrong")
        form = PaymentForm(data={
            'amount': 100,
            'campaign': None,
            'stripe_token': 'xxxx',
        })
        self.assertTrue(form.is_valid())
        with self.assertRaises(ValueError):
            donation = form.make_donation()
            self.assertIsNone(donation)
