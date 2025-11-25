from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login

from ... import signals
from ...views import RegistrationView as BaseRegistrationView


class RegistrationView(BaseRegistrationView):
    """
    A registration backend which implements the simplest possible
    workflow: a user supplies a username, email address and password
    (the bare minimum for a useful account), and is immediately signed
    up and logged in).

    """
    success_url = 'registration_complete'

    def register(self, form):
        new_user = form.save()
        username_field = getattr(new_user, 'USERNAME_FIELD', 'username')
        new_user = authenticate(
            username=getattr(new_user, username_field),
            password=form.cleaned_data['password1']
        )

        login(self.request, new_user)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=self.request)
        return new_user

    def registration_allowed(self):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.

        """
        return getattr(settings, 'REGISTRATION_OPEN', True)
