from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings

@override_settings(AKISMET_API_KEY='')  # Disable Akismet in tests
class ContactFormTests(TestCase):
    def test_foundation_contact(self):
        data = {
            'name': 'A. Random Hacker',
            'email': 'a.random@example.com',
            'message_subject': 'Hello',
            'body': 'Hello, World!'
        }
        resp = self.client.post('/contact/foundation/', data)
        self.assertRedirects(resp, '/contact/sent/')
        self.assertEqual(mail.outbox[-1].subject, '[Contact form] Hello')
