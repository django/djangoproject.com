from django.contrib.auth.models import User
from django.test import TestCase


class TestPermissions(TestCase):
    url = '/markdownx/markdownify/'

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_staff_required(self):
        user = User.objects.create(username='test')
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        user.is_staff = True
        user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
