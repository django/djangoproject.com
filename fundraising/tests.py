from django.test import TestCase

from .models import DjangoHero


class TestIndex(TestCase):
    def test_donors_count(self):
        DjangoHero.objects.create()
        response = self.client.get('/fundraising/')
        self.assertEqual(response.context['total_donors'], 1)
