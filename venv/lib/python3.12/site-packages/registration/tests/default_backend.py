import datetime

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.db import DatabaseError
from django.test import TransactionTestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse
from mock import patch

from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationForm
from registration.models import RegistrationProfile
from registration.users import UserModel


@override_settings(ROOT_URLCONF='test_app.urls_default',
                   ACCOUNT_ACTIVATION_DAYS=7)
class DefaultBackendViewTests(TransactionTestCase):
    """
    Test the default registration backend.

    Running these tests successfully will require two templates to be
    created for the sending of activation emails; details on these
    templates and their contexts may be found in the documentation for
    the default backend.

    """

    registration_profile = RegistrationProfile

    registration_view = RegistrationView

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
        Registration creates a new inactive account and a new profile
        with activation key, populates the correct account data and
        sends an activation email.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})
        self.assertRedirects(resp, reverse('registration_complete'))

        new_user = UserModel().objects.get(username='bob')

        self.assertTrue(new_user.check_password('secret'))
        self.assertEqual(new_user.email, 'bob@example.com')

        # New user must not be active.
        self.assertFalse(new_user.is_active)

        # A registration profile was created, and an activation email
        # was sent.
        self.assertEqual(self.registration_profile.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_registration_no_email(self):
        """
        Overridden Registration view does not send an activation email if the
        associated class variable is set to ``False``

        """
        class RegistrationNoEmailView(self.registration_view):
            SEND_ACTIVATION_EMAIL = False

        request_factory = RequestFactory()
        view = RegistrationNoEmailView.as_view()
        request = request_factory.post('/', data={
            'username': 'bob',
            'email': 'bob@example.com',
            'password1': 'secret',
            'password2': 'secret'})
        request.user = AnonymousUser()

        def dummy_get_response(request):  # pragma: no cover
            return None

        middleware = SessionMiddleware(dummy_get_response)
        middleware.process_request(request)
        view(request)

        UserModel().objects.get(username='bob')
        # A registration profile was created, and no activation email was sent.
        self.assertEqual(self.registration_profile.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(request.session.get('registration_email'), "bob@example.com")

    @override_settings(
        INSTALLED_APPS=('django.contrib.auth', 'registration',)
    )
    def test_registration_no_sites(self):
        """
        Registration still functions properly when
        ``django.contrib.sites`` is not installed; the fallback will
        be a ``RequestSite`` instance.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})
        self.assertEqual(302, resp.status_code)

        new_user = UserModel().objects.get(username='bob')

        self.assertTrue(new_user.check_password('secret'))
        self.assertEqual(new_user.email, 'bob@example.com')

        self.assertFalse(new_user.is_active)

        self.assertEqual(self.registration_profile.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

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
        self.assertEqual(0, len(mail.outbox))

    @patch('registration.models.RegistrationManager.create_inactive_user')
    def test_registration_exception(self, create_inactive_user):
        """
        User is not created beforehand if an exception occurred at
        creating registration profile.
        """
        create_inactive_user.side_effect = DatabaseError()
        valid_data = {'username': 'bob',
                      'email': 'bob@example.com',
                      'password1': 'secret',
                      'password2': 'secret'}
        with self.assertRaises(DatabaseError):
            self.client.post(reverse('registration_register'),
                             data=valid_data)
        assert not UserModel().objects.filter(username='bob').exists()

    def test_activation(self):
        """
        Activation of an account functions properly.

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

    def test_activation_expired(self):
        """
        An expired account can't be activated.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})

        profile = self.registration_profile.objects.get(user__username='bob')
        user = profile.user
        user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS)
        user.save()

        resp = self.client.get(
            reverse('registration_activate',
                    args=(),
                    kwargs={'activation_key': profile.activation_key}))

        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, 'registration/activate.html')
        user = UserModel().objects.get(username='bob')
        self.assertFalse(user.is_active)

    def test_resend_activation(self):
        """
        Resend activation functions properly.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})

        profile = self.registration_profile.objects.get(user__username='bob')

        resp = self.client.post(reverse('registration_resend_activation'),
                                data={'email': profile.user.email})
        self.assertTemplateUsed(resp,
                                'registration/resend_activation_complete.html')
        self.assertEqual(resp.context['email'], profile.user.email)

    def test_resend_activation_invalid_email(self):
        """
        Calling resend with an invalid email shows the same template.

        """
        resp = self.client.post(reverse('registration_resend_activation'),
                                data={'email': 'invalid@example.com'})
        self.assertTemplateUsed(resp,
                                'registration/resend_activation_complete.html')
