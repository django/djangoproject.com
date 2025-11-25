from django.conf import settings
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from registration.forms import RegistrationForm
from registration.users import UserModel


@override_settings(ROOT_URLCONF='test_app.urls_simple')
class SimpleBackendViewTests(TestCase):

    @override_settings(REGISTRATION_OPEN=True)
    def test_registration_open(self):
        """
        The setting ``REGISTRATION_OPEN`` appropriately controls
        whether registration is permitted.

        """
        resp = self.client.get(reverse('registration_register'))
        self.assertEqual(200, resp.status_code)

    @override_settings(REGISTRATION_OPEN=False)
    def test_registration_closed(self):

        # Now all attempts to hit the register view should redirect to
        # the 'registration is closed' message.
        resp = self.client.get(reverse('registration_register'))
        self.assertRedirects(resp, reverse('registration_disallowed'))

        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})
        self.assertRedirects(resp, reverse('registration_disallowed'))

    def test_registration_get(self):
        """
        HTTP ``GET`` to the registration view uses the appropriate
        template and populates a registration form into the context.

        """
        resp = self.client.get(reverse('registration_register'))
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp,
                                'registration/registration_form.html')
        self.assertIsInstance(resp.context['form'], RegistrationForm)

    def test_registration(self):
        """
        Registration creates a new account and logs the user in.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})
        new_user = UserModel().objects.get(username='bob')
        self.assertEqual(302, resp.status_code)
        self.assertIn(getattr(settings, 'SIMPLE_BACKEND_REDIRECT_URL', '/'),
                      resp['Location'])

        self.assertTrue(new_user.check_password('secret'))
        self.assertEqual(new_user.email, 'bob@example.com')

        # New user must be active.
        self.assertTrue(new_user.is_active)

        # New user must be logged in.
        resp = self.client.get(reverse('registration_register'), follow=True)
        self.assertTrue(resp.context['user'].is_authenticated)

    def test_registration_failure(self):
        """
        Registering with invalid data fails.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'notsecret'})
        self.assertEqual(200, resp.status_code)
        self.assertFalse(resp.context['form'].is_valid())
