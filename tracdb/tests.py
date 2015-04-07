from django.test import TestCase

from .models import Revision


class TestModels(TestCase):
    def test_router(self):
        self.assertEqual(Revision.objects.db, 'trac')
