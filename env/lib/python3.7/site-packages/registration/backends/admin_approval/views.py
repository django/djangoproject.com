from django.contrib.sites.shortcuts import get_current_site

from ... import signals
from ...models import SupervisedRegistrationProfile
from ...views import ApprovalView as BaseApprovalView
from ..default.views import ActivationView as BaseActivationView
from ..default.views import RegistrationView as BaseRegistrationView
from ..default.views import ResendActivationView as BaseResendActivationView


class RegistrationView(BaseRegistrationView):

    """
    Follows the exact logic of
    ``registration.backends.default.views.RegistrationView`` but uses
    ``SupervisedRegistrationProfile`` instead of ``RegistrationProfile``

    """

    registration_profile = SupervisedRegistrationProfile


class ActivationView(BaseActivationView):

    """
    Follows the exact logic of
    ``registration.backends.default.views.ActivationView`` but uses
    ``SupervisedRegistrationProfile`` instead of ``RegistrationProfile``

    """

    registration_profile = SupervisedRegistrationProfile


class ResendActivationView(BaseResendActivationView):

    """
    Follows the exact logic of
    ``registration.backends.default.views.ResendActivationView`` but uses
    ``SupervisedRegistrationProfile`` instead of ``RegistrationProfile``

    """

    registration_profile = SupervisedRegistrationProfile


class ApprovalView(BaseApprovalView):
    def approve(self, *args, **kwargs):
        """
        Given a user id, look up and approve the user account
        corresponding to that key (if possible).

        After successful approval, the signal
        ``registration.signals.user_approved`` will be sent, with the
        newly approved ``User`` as the keyword argument ``user`` and
        the class of this backend as the sender.

        """
        user_id = kwargs.get('profile_id', '')
        approved_user = (
            SupervisedRegistrationProfile.objects.admin_approve_user(
                user_id, get_current_site(self.request)))
        if approved_user:
            signals.user_approved.send(
                sender=self.__class__,
                user=approved_user,
                request=self.request
            )
        return approved_user

    def get_success_url(self, user):
        return ('registration_approve_complete', (), {})
