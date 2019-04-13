from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render

from ... import signals
from ...models import RegistrationProfile
from ...users import UserModel
from ...views import ActivationView as BaseActivationView
from ...views import RegistrationView as BaseRegistrationView
from ...views import ResendActivationView as BaseResendActivationView


class RegistrationView(BaseRegistrationView):
    """
    A registration backend which follows a simple workflow:

    1. User signs up, inactive account is created.

    2. Email is sent to user with activation link.

    3. User clicks activation link, account is now active.

    Using this backend requires that

    * ``registration`` be listed in the ``INSTALLED_APPS`` setting
      (since this backend makes use of models defined in this
      application).

    * The setting ``ACCOUNT_ACTIVATION_DAYS`` be supplied, specifying
      (as an integer) the number of days from registration during
      which a user may activate their account (after that period
      expires, activation will be disallowed).

    * The creation of the templates
      ``registration/activation_email_subject.txt`` and
      ``registration/activation_email.txt``, which will be used for
      the activation email. See the notes for this backends
      ``register`` method for details regarding these templates.

    When subclassing this view, you can set the ``SEND_ACTIVATION_EMAIL``
    class variable to False to skip sending the new user a confirmation
    email or set ``SEND_ACTIVATION_EMAIL`` to ``False``. Doing so implies
    that you will have to activate the user manually from the admin site or
    send an activation by some other method. For example, by listening for
    the ``user_registered`` signal.

    Additionally, registration can be temporarily closed by adding the
    setting ``REGISTRATION_OPEN`` and setting it to
    ``False``. Omitting this setting, or setting it to ``True``, will
    be interpreted as meaning that registration is currently open and
    permitted.

    Internally, this is accomplished via storing an activation key in
    an instance of ``registration.models.RegistrationProfile``. See
    that model and its custom manager for full documentation of its
    fields and supported operations.

    """
    SEND_ACTIVATION_EMAIL = getattr(settings, 'SEND_ACTIVATION_EMAIL', True)
    success_url = 'registration_complete'

    registration_profile = RegistrationProfile

    def register(self, form):
        """
        Given a username, email address and password, register a new
        user account, which will initially be inactive.

        Along with the new ``User`` object, a new
        ``registration.models.RegistrationProfile`` will be created,
        tied to that ``User``, containing the activation key which
        will be used for this account.

        An email will be sent to the supplied email address; this
        email should contain an activation link. The email will be
        rendered using two templates. See the documentation for
        ``RegistrationProfile.send_activation_email()`` for
        information about these templates and the contexts provided to
        them.

        After the ``User`` and ``RegistrationProfile`` are created and
        the activation email is sent, the signal
        ``registration.signals.user_registered`` will be sent, with
        the new ``User`` as the keyword argument ``user`` and the
        class of this backend as the sender.

        """
        site = get_current_site(self.request)

        if hasattr(form, 'save'):
            new_user_instance = form.save()
        else:
            new_user_instance = (UserModel().objects
                                 .create_user(**form.cleaned_data))

        new_user = self.registration_profile.objects.create_inactive_user(
            new_user=new_user_instance,
            site=site,
            send_email=self.SEND_ACTIVATION_EMAIL,
            request=self.request,
        )
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


class ActivationView(BaseActivationView):

    registration_profile = RegistrationProfile

    def activate(self, *args, **kwargs):
        """
        Given an an activation key, look up and activate the user
        account corresponding to that key (if possible).

        After successful activation, the signal
        ``registration.signals.user_activated`` will be sent, with the
        newly activated ``User`` as the keyword argument ``user`` and
        the class of this backend as the sender.

        """
        activation_key = kwargs.get('activation_key', '')
        site = get_current_site(self.request)
        user, activated = self.registration_profile.objects.activate_user(
            activation_key, site)
        if activated:
            signals.user_activated.send(sender=self.__class__,
                                        user=user,
                                        request=self.request)
        return user

    def get_success_url(self, user):
        return ('registration_activation_complete', (), {})


class ResendActivationView(BaseResendActivationView):

    registration_profile = RegistrationProfile

    def resend_activation(self, form):
        """
        Given an email, look up user by email and resend activation key
        if user is not already activated or previous activation key has
        not expired. Note that if multiple users exist with the given
        email, no emails will be sent.

        Returns True if activation key was successfully sent, False otherwise.

        """
        site = get_current_site(self.request)
        email = form.cleaned_data['email']
        return self.registration_profile.objects.resend_activation_mail(
            email, site, self.request)

    def render_form_submitted_template(self, form):
        """
        Renders resend activation complete template with the submitted email.

        """
        email = form.cleaned_data['email']
        context = {'email': email}
        return render(self.request,
                      'registration/resend_activation_complete.html',
                      context)
