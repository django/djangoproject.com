from django.test.utils import override_settings
from django.urls import reverse

from .default_backend import DefaultBackendViewTests

from registration.backends.admin_approval.views import RegistrationView
from registration.models import SupervisedRegistrationProfile
from registration.users import UserModel


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
        user = profile.user
        # fail if the user is active (this should not happen yet)
        self.failIf(not user.is_active)
        self.assertRedirects(resp, reverse('registration_approve_complete'))
