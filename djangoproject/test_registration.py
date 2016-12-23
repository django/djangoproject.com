from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import mail
from django.test import TestCase
from registration.models import RegistrationProfile


class TestRegistration(TestCase):
    def test_activation_email(self):
        site = Site.objects.get()
        user = User(email='test@example.com')
        profile = RegistrationProfile(user=user, activation_key='activation-key')
        profile.send_activation_email(site)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox.pop()
        self.assertEqual(message.subject, 'Activate your djangoproject.com account')
        self.assertEqual(
            message.body,
            "\nSomeone, hopefully you, signed up for a new account at "
            "djangoproject.com using this email address. If it was you, and "
            "you'd like to activate and use your account, click the link below "
            "or copy and paste it into your web browser's address bar:\n\n"
            "https://www.djangoproject.com/accounts/activate/activation-key/\n\n"
            "If you didn't request this, you don't need to do anything; you "
            "won't receive any more email from us, and the account will expire "
            "automatically in three days.\n"
        )
