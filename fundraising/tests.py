from datetime import date, timedelta
from decimal import Decimal
from operator import attrgetter

from django.test import TestCase

from .models import DjangoHero, Donation


class TestIndex(TestCase):
    def test_donors_count(self):
        DjangoHero.objects.create()
        response = self.client.get('/fundraising/')
        self.assertEqual(response.context['total_donors'], 1)


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
