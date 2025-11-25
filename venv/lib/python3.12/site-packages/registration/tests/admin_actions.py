from django.contrib.admin import helpers
from django.core import mail
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.urls import reverse

from registration.models import RegistrationProfile
from registration.users import UserModel


@override_settings(ACCOUNT_ACTIVATION_DAYS=7,
                   REGISTRATION_DEFAULT_FROM_EMAIL='registration@email.com',
                   REGISTRATION_EMAIL_HTML=True,
                   DEFAULT_FROM_EMAIL='django@email.com')
class AdminCustomActionsTestCase(TestCase):
    """
    Test the available admin custom actions
    """

    def setUp(self):
        self.client = Client()
        admin_user = UserModel().objects.create_superuser(
            'admin', 'admin@test.com', 'admin')
        self.client.login(username=admin_user.get_username(), password=admin_user)

        self.user_info = {'username': 'alice',
                          'password': 'swordfish',
                          'email': 'alice@example.com'}

    def test_activate_users(self):
        """
        Test the admin custom command 'activate users'

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)

        self.assertFalse(profile.activated)

        registrationprofile_list = reverse(
            'admin:registration_registrationprofile_changelist')
        post_data = {
            'action': 'activate_users',
            helpers.ACTION_CHECKBOX_NAME: [profile.pk],
        }
        self.client.post(registrationprofile_list, post_data, follow=True)

        profile = RegistrationProfile.objects.get(user=new_user)
        self.assertTrue(profile.activated)

    def test_resend_activation_email(self):
        """
        Test the admin custom command 'resend activation email'
        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)

        registrationprofile_list = reverse(
            'admin:registration_registrationprofile_changelist')
        post_data = {
            'action': 'resend_activation_email',
            helpers.ACTION_CHECKBOX_NAME: [profile.pk],
        }
        self.client.post(registrationprofile_list, post_data, follow=True)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])
