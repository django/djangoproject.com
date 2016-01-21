from django.test import TestCase, override_settings


@override_settings(ROOT_URLCONF='legacy.urls')
class LegacyTests(TestCase):

    def test_gone(self):
        response = self.client.get('/comments/')
        self.assertEqual(response.status_code, 410)
