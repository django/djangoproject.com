from django.conf import settings
from django.core import mail
from django.test.utils import override_settings
from django.urls import reverse

from .default_backend import DefaultBackendViewTests

from registration.backends.admin_approval.views import RegistrationView
from registration.models import SupervisedRegistrationProfile
from registration.users import UserModel


def get_registration_admins():
    """
    Mock function for testing the admin getter functionality

    """
    return [
        ("Functional admin 1", "func_admin1@fakemail.com"),
        ("Functional admin 2", "func_admin2@fakemail.com")
    ]


@override_settings(ROOT_URLCONF='test_app.urls_admin_approval')
class AdminApprovalBackendViewTests(DefaultBackendViewTests):
    """
    Test the admin_approval registration backend.

    Running these tests successfully will require two templates to be
    created for the sending of activation emails; details on these
    templates and their contexts may be found in the documentation for
    the default backend.

    """

    registration_profile = SupervisedRegistrationProfile

    registration_view = RegistrationView

    def test_approval(self):
        """
        Approval of an account functions properly.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})

        profile = self.registration_profile.objects.get(user__username='bob')
        self.assertFalse(profile.user.is_active)

        resp = self.client.get(
            reverse('registration_activate',
                    args=(),
                    kwargs={'activation_key': profile.activation_key}))

        admin_user = UserModel().objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.client.login(username=admin_user.get_username(), password=admin_user)

        resp = self.client.get(
            reverse('registration_admin_approve',
                    args=(),
                    kwargs={'profile_id': profile.id}))
        profile.user.refresh_from_db()
        self.assertTrue(profile.user.is_active)
        self.assertRedirects(resp, reverse('registration_approve_complete'))

    @override_settings(
        REGISTRATION_ADMINS=[
            ("The admin", "admin_alpha@fakemail.com"),
            ("The other admin", "admin_two@fakemail.com")
        ]
    )
    def test_admins_when_is_list(self):
        """
        Admins are pulled from the REGISTRATION_ADMINS list setting
        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})

        profile = self.registration_profile.objects.get(user__username='bob')

        resp = self.client.get(
            reverse('registration_activate',
                    args=(),
                    kwargs={'activation_key': profile.activation_key}))
        self.assertRedirects(resp, reverse('registration_activation_complete'))
        admins_mail = mail.outbox[1]
        self.assertEqual(admins_mail.to, [to[1] for to in settings.REGISTRATION_ADMINS])

    @override_settings(
        REGISTRATION_ADMINS="registration.tests.admin_approval_backend.get_registration_admins"
    )
    def test_admins_when_is_getter(self):
        """
        Admins are pulled from the REGISTRATION_ADMINS string setting
        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})

        profile = self.registration_profile.objects.get(user__username='bob')

        resp = self.client.get(
            reverse('registration_activate',
                    args=(),
                    kwargs={'activation_key': profile.activation_key}))
        self.assertRedirects(resp, reverse('registration_activation_complete'))
        admins_mail = mail.outbox[1]
        self.assertEqual(admins_mail.to, [to[1] for to in get_registration_admins()])
