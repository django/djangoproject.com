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

    def test_coc_contact(self):
        data = {
            'name': 'A. Random Hacker',
            'email': 'a.random@example.com',
            'body': 'Hello, World'
        }
        resp = self.client.post('/contact/code-of-conduct/', data)
        self.assertRedirects(resp, '/conduct/')
        self.assertEqual(mail.outbox[-1].subject, 'Django Code of Conduct feedback')

    def test_coc_contact_unicode(self):
        data = {
            'name': 'A. Random Hacker',
            'email': 'a.random@example.com',
            'body': u'Hello, \u2603!'
        }
        resp = self.client.post('/contact/code-of-conduct/', data)
        self.assertRedirects(resp, '/conduct/')
