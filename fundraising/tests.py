from datetime import date, timedelta
from decimal import Decimal
from mock import patch
from operator import attrgetter

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from .forms import PaymentForm
from .models import DjangoHero, Donation

class TestIndex(TestCase):
    def test_donors_count(self):
        DjangoHero.objects.create()
        response = self.client.get(reverse('fundraising:index'))
        self.assertEqual(response.context['total_donors'], 1)

    def test_render_donate_form_with_amount(self):
        response = self.client.get(reverse('fundraising:donate'), {'amount': 50})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['fixed_amount'], '50')
        self.assertEqual(response.context['publishable_key'], settings.STRIPE_PUBLISHABLE_KEY)

        # Checking if amount field is hidden
        self.assertIsInstance(response.context['form'].fields['amount'].widget, forms.HiddenInput)
        # Checking if campaign field is empty
        self.assertEqual(response.context['form'].initial['campaign'], None)

    def test_render_donate_form_without_amount(self):
        response = self.client.get(reverse('fundraising:donate'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['fixed_amount'], None)
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
            self.assertEqual(response.context['fixed_amount'], '100')
            self.assertEqual(response.context['publishable_key'], settings.STRIPE_PUBLISHABLE_KEY)

            # Checking if amount field is hidden
            self.assertIsInstance(response.context['form'].fields['amount'].widget, forms.HiddenInput)
            # Checking if campaign field is same as campaign
            self.assertEqual(response.context['form'].initial['campaign'], campaign)

    def test_submitting_donation_form_invalid(self):
        url = reverse('fundraising:donate')
        response = self.client.post(url, {'amount': 100})
        self.assertFalse(response.context['form'].is_valid())
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'fundraising/donate.html')

    def test_submitting_donation_form(self):
        response = self.client.post(reverse('fundraising:donate'), {'amount': 100})
        self.assertFalse(response.context['form'].is_valid())

        with patch('stripe.Customer.create', id='test'):
            with patch('stripe.Charge.create', id='test'):
                response = self.client.post(reverse('fundraising:donate'), {
                    'amount': 100,
                    'stripe_token': 'test',
                })
                donations = Donation.objects.all()
                self.assertEqual(donations.count(), 1)
                self.assertEqual(donations[0].amount, 100)
                self.assertEqual(donations[0].campaign_name, '')

    def test_submitting_donation_form_with_campaign(self):
        response = self.client.post(reverse('fundraising:donate'), {
            'amount': 100,
            'campaign': 'test',
        })
        self.assertFalse(response.context['form'].is_valid())

        with patch('stripe.Customer.create', id='test'):
            with patch('stripe.Charge.create', id='test'):
                response = self.client.post(reverse('fundraising:donate'), {
                    'amount': 100,
                    'campaign': 'test',
                    'stripe_token': 'test',
                })
                donations = Donation.objects.all()
                self.assertEqual(donations.count(), 1)
                self.assertEqual(donations[0].amount, 100)
                self.assertEqual(donations[0].campaign_name, 'test')

    @patch('fundraising.forms.PaymentForm.make_donation')
    def test_submitting_donation_form_valid_bad_request(self, make_donation):
        make_donation.return_value = None
        response = self.client.post(reverse('fundraising:donate'), {
            'amount': 100,
            'campaign': None,
            'stripe_token': 'xxxx',
        })
        self.assertEqual(400, response.status_code)

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
    def test_in_period_ordering(self):
        kwargs = {
            'approved': True,
            'is_visible': True,
            'is_amount_displayed': True,
        }
        h1 = DjangoHero.objects.create(**kwargs)
        Donation.objects.create(donor=h1, amount='5')
        h2 = DjangoHero.objects.create(**kwargs)
        Donation.objects.create(donor=h2, amount='15')
        # hidden donation amount should display last
        kwargs['is_amount_displayed'] = False
        h3 = DjangoHero.objects.create(**kwargs)
        Donation.objects.create(donor=h3, amount='10')
        today = date.today()
        self.assertQuerysetEqual(
            DjangoHero.objects.in_period(today, today + timedelta(days=1)),
            [Decimal('15.00'), Decimal('5.00'), Decimal('10.00')],
            attrgetter('donated_amount')
        )


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
        donation = form.make_donation()
        self.assertIsNone(donation)
