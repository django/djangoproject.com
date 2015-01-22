from datetime import date, timedelta
from functools import partial
from mock import patch
from operator import attrgetter

from django.test import TestCase

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
        response = self.client.get('/fundraising/')
        self.assertEqual(response.context['total_donors'], 1)


class TestDjangoHero(TestCase):
    def setUp(self):
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
        self.today = date.today()

    def test_donation_suffling(self):
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
