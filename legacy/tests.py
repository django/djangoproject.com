from django.test import TestCase


class LegacyTests(TestCase):
    urls = 'legacy.urls'

    # Just a smoke test to ensure the URLconf works

    def test_gone(self):
        response = self.client.get('/comments/')
        self.assertEquals(response.status_code, 410)
