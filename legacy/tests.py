from django.test import TestCase, override_settings


@override_settings(ROOT_URLCONF='legacy.urls')
class LegacyTests(TestCase):

    def test_gone(self):
        response = self.client.get('/comments/')
        self.assertEqual(response.status_code, 410)

    def test_400(self):
        response = self.client.get('/400/')
        self.assertContains(response, 'Bad request', status_code=400)

    def test_403(self):
        response = self.client.get('/403/')
        self.assertContains(response, 'Permission denied', status_code=403)

    def test_404(self):
        response = self.client.get('/404/')
        self.assertContains(response, 'Page not found', status_code=404)

    def test_500(self):
        response = self.client.get('/500/')
        self.assertContains(response, 'Page unavailable', status_code=500)
