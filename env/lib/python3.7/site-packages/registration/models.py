from __future__ import unicode_literals

import datetime
import hashlib
import logging
import re
import string
import warnings

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db import transaction
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now as datetime_now
from django.utils.translation import ugettext_lazy as _

from .users import UserModel
from .users import UserModelString

logger = logging.getLogger(__name__)
SHA1_RE = re.compile('^[a-f0-9]{40}$')


def get_from_email(site=None):
    """
    Return the email address by which mail is sent.
    If the `REGISTRATION_USE_SITE_EMAIL` setting is set, the `Site` object will
    provide the domain and the REGISTRATION_SITE_USER_EMAIL will provide the
    username. Otherwise the `REGISTRATION_DEFAULT_FROM_EMAIL` or
    `DEFAULT_FROM_EMAIL` settings are used.
    """
    if getattr(settings, 'REGISTRATION_USE_SITE_EMAIL', False):
        user_email = getattr(settings, 'REGISTRATION_SITE_USER_EMAIL', None)
        if not user_email:
            raise ImproperlyConfigured((
                'REGISTRATION_SITE_USER_EMAIL must be set when using '
                'REGISTRATION_USE_SITE_EMAIL.'))
        Site = apps.get_model('sites', 'Site')
        site = site or Site.objects.get_current()
        from_email = '{}@{}'.format(user_email, site.domain)
    else:
        from_email = getattr(settings, 'REGISTRATION_DEFAULT_FROM_EMAIL',
                             settings.DEFAULT_FROM_EMAIL)
    return from_email


def send_email(addresses_to, ctx_dict, subject_template, body_template,
               body_html_template):
    """
    Function that sends an email
    """

    prefix = getattr(settings, 'REGISTRATION_EMAIL_SUBJECT_PREFIX', '')
    subject = prefix + render_to_string(subject_template, ctx_dict)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    from_email = get_from_email(ctx_dict.get('site'))
    message_txt = render_to_string(body_template,
                                   ctx_dict)

    email_message = EmailMultiAlternatives(subject, message_txt,
                                           from_email, addresses_to)

    if getattr(settings, 'REGISTRATION_EMAIL_HTML', True):
        try:
            message_html = render_to_string(
                body_html_template, ctx_dict)
        except TemplateDoesNotExist:
            pass
        else:
            email_message.attach_alternative(message_html, 'text/html')

    email_message.send()


class RegistrationManager(models.Manager):
    """
    Custom manager for the ``RegistrationProfile`` model.

    The methods defined here provide shortcuts for account creation
    and activation (including generation and emailing of activation
    keys), and for cleaning out expired inactive accounts.

    """

    def _activate(self, profile, site, get_profile):
        """
        Activate the ``RegistrationProfile`` given as argument.
        User is able to login, as ``is_active`` is set to ``True``
        """
        user = profile.user
        user.is_active = True
        profile.activated = True

        with transaction.atomic():
            user.save()
            profile.save()
        if get_profile:
            return profile
        else:
            return user

    def activate_user(self, activation_key, site, get_profile=False):
        """
        Validate an activation key and activate the corresponding ``User`` if
        valid, returns a tuple of (``User``, ``activated``). The activated flag
        indicates if the user was newly activated or an error occurred.

        If the key is valid and has not expired, return the (``User``,
        ``True``) after activating.

        If the key is not valid or has expired, return (``User`` or ``False``,
        ``False``).

        If the key is valid but the ``User`` is already active,
        return (``User``, ``False``).

        If the key is valid but the ``User`` is inactive, return (``User``,
        ``False``).

        To prevent reactivation of an account which has been
        deactivated by site administrators, ``RegistrationProfile.activated``
        is set to ``True`` after successful activation.

        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                # This is an actual activation failure as the activation
                # key does not exist. It is *not* the scenario where an
                # already activated User reuses an activation key.
                return (False, False)

            if profile.activated:
                # The User has already activated and is trying to activate
                # again. If the User is active, return the User. Else,
                # return False as the User has been deactivated by a site
                # administrator.
                if profile.user.is_active:
                    return (profile.user, False)
                else:
                    return (profile.user, False)

            if not profile.activation_key_expired():
                return (self._activate(profile, site, get_profile), True)

        return (False, False)

    def create_inactive_user(self, site, new_user=None, send_email=True,
                             request=None, profile_info={}, **user_info):
        """
        Create a new, inactive ``User``, generate a
        ``RegistrationProfile`` and email its activation key to the
        ``User``, returning the new ``User``.

        By default, an activation email will be sent to the new
        user. To disable this, pass ``send_email=False``.
        Additionally, if email is sent and ``request`` is supplied,
        it will be passed to the email template.

        """
        if new_user is None:
            password = user_info.pop('password')
            new_user = UserModel()(**user_info)
            new_user.set_password(password)
        new_user.is_active = False

        # Since we calculate the RegistrationProfile expiration from this date,
        # we want to ensure that it is current
        new_user.date_joined = datetime_now()

        with transaction.atomic():
            new_user.save()
            registration_profile = self.create_profile(
                new_user, **profile_info)

        if send_email:
            registration_profile.send_activation_email(site, request)

        return new_user

    def create_profile(self, user, **profile_info):
        """
        Create a ``RegistrationProfile`` for a given
        ``User``, and return the ``RegistrationProfile``.

        The activation key for the ``RegistrationProfile`` will be a
        SHA1 hash, generated from a secure random string.

        """
        profile = self.model(user=user, **profile_info)

        if 'activation_key' not in profile_info:
            profile.create_new_activation_key(save=False)

        profile.save()

        return profile

    def resend_activation_mail(self, email, site, request=None):
        """
        Resets activation key for the user and resends activation email.
        """
        try:
            profile = self.get(user__email__iexact=email)
        except ObjectDoesNotExist:
            return False
        except MultipleObjectsReturned:
            return False

        if profile.activated or profile.activation_key_expired():
            return False

        profile.create_new_activation_key()
        profile.send_activation_email(site, request)

        return True

    def delete_expired_users(self):
        """
        Remove expired instances of ``RegistrationProfile`` and their
        associated ``User``s.

        Accounts to be deleted are identified by searching for instances of
        ``RegistrationProfile`` with expired activation keys and an
        ``activated`` field that is set to ``False``. If these conditions are
        met both the ``RegistrationProfile`` and the ``User`` objects will be
        deleted.

        It is recommended that this method be executed regularly as
        part of your routine site maintenance; this application
        provides a custom management command which will call this
        method, accessible as ``manage.py cleanupregistration``.

        Regularly clearing out accounts which have never been
        activated serves two useful purposes:

        1. It alleviates the ocasional need to reset a
           ``RegistrationProfile`` and/or re-send an activation email
           when a user does not receive or does not act upon the
           initial activation email; since the account will be
           deleted, the user will be able to simply re-register and
           receive a new activation key.

        2. It prevents the possibility of a malicious user registering
           one or more accounts and never activating them (thus
           denying the use of those usernames to anyone else); since
           those accounts will be deleted, the usernames will become
           available for use again.

        If you have a troublesome ``User`` and wish to disable their
        account while keeping it in the database, simply delete the
        associated ``RegistrationProfile``; an inactive ``User`` which
        does not have an associated ``RegistrationProfile`` will not
        be deleted.

        """
        profiles = self.filter(
            models.Q(user__is_active=False) | models.Q(user=None),
            activated=False,
        )
        for profile in profiles:
            try:
                if profile.activation_key_expired():
                    user = profile.user
                    logger.warning('Deleting expired Registration profile {} and user {}.'.format(profile, user))
                    profile.delete()
                    user.delete()
            except UserModel().DoesNotExist:
                logger.warning('Deleting expired Registration profile'.format(profile))
                profile.delete()


@python_2_unicode_compatible
class RegistrationProfile(models.Model):
    """
    A simple profile which stores an activation key for use during
    user account registration.

    Generally, you will not want to interact directly with instances
    of this model; the provided manager includes methods
    for creating and activating new accounts, as well as for cleaning
    out accounts which have never been activated.

    While it is possible to use this model as the value of the
    ``AUTH_PROFILE_MODULE`` setting, it's not recommended that you do
    so. This model's sole purpose is to store data temporarily during
    account registration and activation.

    """
    user = models.OneToOneField(
        UserModelString(),
        on_delete=models.CASCADE,
        verbose_name=_('user'),
    )
    activation_key = models.CharField(_('activation key'), max_length=40)
    activated = models.BooleanField(default=False)

    objects = RegistrationManager()

    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')

    def __str__(self):
        return "Registration information for %s" % self.user

    def create_new_activation_key(self, save=True):
        """
        Create a new activation key for the user
        """
        random_string = get_random_string(
            length=32, allowed_chars=string.printable)
        self.activation_key = hashlib.sha1(
            random_string.encode('utf-8')).hexdigest()

        if save:
            self.save()

        return self.activation_key

    def activation_key_expired(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.

        Key expiration is determined by a two-step process:

        1. If the user has already activated, ``self.activated`` will
           be ``True``. Re-activating is not permitted, and so this
           method returns ``True`` in this case.

        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.

        """
        max_expiry_days = datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS)
        expiration_date = self.user.date_joined + max_expiry_days
        return self.activated or expiration_date <= datetime_now()

    def send_activation_email(self, site, request=None):
        """
        Send an activation email to the user associated with this
        ``RegistrationProfile``.

        The activation email will use the following templates,
        which can be overriden by setting ACTIVATION_EMAIL_SUBJECT,
        ACTIVATION_EMAIL_BODY, and ACTIVATION_EMAIL_HTML appropriately:

        ``registration/activation_email_subject.txt``
            This template will be used for the subject line of the
            email. Because it is used as the subject line of an email,
            this template's output **must** be only a single line of
            text; output longer than one line will be forcibly joined
            into only a single line.

        ``registration/activation_email.txt``
            This template will be used for the text body of the email.

        ``registration/activation_email.html``
            This template will be used for the html body of the email.

        These templates will each receive the following context
        variables:

        ``user``
            The new user account

        ``activation_key``
            The activation key for the new account.

        ``expiration_days``
            The number of days remaining during which the account may
            be activated.

        ``site``
            An object representing the site on which the user
            registered; depending on whether ``django.contrib.sites``
            is installed, this may be an instance of either
            ``django.contrib.sites.models.Site`` (if the sites
            application is installed) or
            ``django.contrib.sites.requests.RequestSite`` (if
            not). Consult the documentation for the Django sites
            framework for details regarding these objects' interfaces.

        ``request``
            Optional Django's ``HttpRequest`` object from view.
            If supplied will be passed to the template for better
            flexibility via ``RequestContext``.
        """
        activation_email_subject = getattr(settings, 'ACTIVATION_EMAIL_SUBJECT',
                                           'registration/activation_email_subject.txt')
        activation_email_body = getattr(settings, 'ACTIVATION_EMAIL_BODY',
                                        'registration/activation_email.txt')
        activation_email_html = getattr(settings, 'ACTIVATION_EMAIL_HTML',
                                        'registration/activation_email.html')

        ctx_dict = {
            'user': self.user,
            'activation_key': self.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': site,
        }
        prefix = getattr(settings, 'REGISTRATION_EMAIL_SUBJECT_PREFIX', '')
        subject = prefix + render_to_string(
            activation_email_subject, ctx_dict, request=request
        )

        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        from_email = get_from_email(site)
        message_txt = render_to_string(activation_email_body,
                                       ctx_dict, request=request)

        email_message = EmailMultiAlternatives(subject, message_txt,
                                               from_email, [self.user.email])

        if getattr(settings, 'REGISTRATION_EMAIL_HTML', True):
            try:
                message_html = render_to_string(
                    activation_email_html, ctx_dict, request=request)
            except TemplateDoesNotExist:
                pass
            else:
                email_message.attach_alternative(message_html, 'text/html')

        email_message.send()


class SupervisedRegistrationManager(RegistrationManager):

    def activation_key_expired(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.

        Key expiration is determined by a two-step process:

        1. If the user has already activated, ``self.activated`` and
        `self.user.is_active`` will be ``True``.  Re-activating is not
        permitted, and so this method returns ``True`` in this case.

        2. Otherwise, the date the user signed up is incremented by the number
        of days specified in the setting ``ACCOUNT_ACTIVATION_DAYS`` (which
        should be the number of days after signup during which a user is
        allowed to activate their account); if the result is less than or equal
        to the current date, the key has expired and this method returns
        ``True``.
        """
        expiration_date = datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS)
        # A user is only considered activated when the entire registration
        # process is completed (i.e. an admin has approved the account)
        is_activated = self.activated and self.user.is_active
        return (is_activated or self.user.date_joined + expiration_date <= datetime_now())

    def _activate(self, profile, site, get_profile):
        """
        Activate the ``SupervisedRegistrationProfile`` given as argument.

        Send an email to the site administrators to approve the user.

        User is not able to login yet, as ``is_active`` is not yet ``True``
        """

        if not profile.user.is_active and not profile.activated:
            self.send_admin_approve_email(profile.user, site)

        # do not set ``User.is_active`` as True. This will be set
        # when a site administrator approves this account.
        profile.activated = True
        profile.save()
        if get_profile:
            return profile
        else:
            return profile.user

    def admin_approve_user(self, profile_id, site, get_profile=False, request=None):
        """
        Approve the ``SupervisedRegistrationProfile``
        object with the given ``profile_id``.

        If the id is valid, return the ``User``
        after approving.

        If the id is not valid, return ``False``.

        If the id is valid but the ``User`` is already active,
        return ``User``.

        If the id is valid but the ``SupervisedRegistrationProfile``
        object is not activated, return ``False``.
        """
        try:
            profile = SupervisedRegistrationProfile.objects.get(id=profile_id)
            if profile.activated:
                if profile.user.is_active:
                    return profile.user

            # If the user has not activated their profile the admin should
            # not be able to approve his account (at least not following
            # this process)
            if profile.activated:
                profile.user.is_active = True
            else:
                return False

            profile.user.save()
            profile.send_admin_approve_complete_email(site, request)

            if get_profile:
                return profile
            else:
                return profile.user
        except self.model.DoesNotExist:
            return False

    def send_admin_approve_email(self, user, site, request=None):
        """
        Send an approval email to the site administrators to
        approve this user.

        The approval email will use the following templates,
        which can be overriden by setting APPROVAL_EMAIL_SUBJECT,
        APPROVAL_EMAIL_BODY, and APPROVAL_EMAIL_HTML appropriately:

        ``registration/admin_approve_email_subject.txt``
            This template will be used for the subject line of the
            email. Because it is used as the subject line of an email,
            this template's output **must** be only a single line of
            text; output longer than one line will be forcibly joined
            into only a single line.

        ``registration/admin_approve_email.txt``
            This template will be used for the text body of the email.

        ``registration/admin_approve_email.html``
            This template will be used for the html body of the email.

        These templates will each receive the following context
        variables:

        ``user``
            The new user account

        ``profile_id``
            The id of the associated``SupervisedRegistrationProfile``
            object.

        ``site``
            An object representing the site on which the user
            registered; depending on whether ``django.contrib.sites``
            is installed, this may be an instance of either
            ``django.contrib.sites.models.Site`` (if the sites
            application is installed) or
            ``django.contrib.sites.requests.RequestSite`` (if
            not). Consult the documentation for the Django sites
            framework for details regarding these objects' interfaces.

        ``request``
            Optional Django's ``HttpRequest`` object from view.
            If supplied will be passed to the template for better
            flexibility via ``RequestContext``.
        """

        admin_approve_email_subject = getattr(
            settings,
            'ADMIN_APPROVAL_EMAIL_SUBJECT',
            'registration/admin_approve_email_subject.txt'
        )
        admin_approve_email_body = getattr(
            settings,
            'ADMIN_APPROVAL_EMAIL_BODY',
            'registration/admin_approve_email.txt'
        )
        admin_approve_email_html = getattr(
            settings,
            'ADMIN_APPROVAL_EMAIL_HTML',
            'registration/admin_approve_email.html'
        )

        ctx_dict = {
            'user': user,
            'profile_id': user.registrationprofile.id,
            'site': site,
        }
        registration_admins = getattr(settings, 'REGISTRATION_ADMINS', None)
        admins = registration_admins or getattr(settings, 'ADMINS', None)

        if not registration_admins:
            warnings.warn('No registration admin defined in'
                          ' settings.REGISTRATION_ADMINS.'
                          ' Using settings.ADMINS for the admin approval',
                          UserWarning)
        if not admins:
            raise ImproperlyConfigured(
                'Using the admin_approval registration backend'
                ' requires at least one admin in settings.ADMINS'
                ' or settings.REGISTRATION_ADMINS')

        admins = [admin[1] for admin in admins]
        send_email(
            admins, ctx_dict, admin_approve_email_subject,
            admin_approve_email_body, admin_approve_email_html
        )


class SupervisedRegistrationProfile(RegistrationProfile):

    # Same model as ``RegistrationProfile``, just a different
    # Manager to implement the extra functionality required
    # in admin approval
    objects = SupervisedRegistrationManager()

    def send_admin_approve_complete_email(self, site, request=None):
        """
        Send an "approval is complete" email to the user associated with this
        ``SupervisedRegistrationProfile``.

        The email will use the following templates,
        which can be overriden by settings APPROVAL_COMPLETE_EMAIL_SUBJECT,
        APPROVAL_COMPLETE_EMAIL_BODY, and APPROVAL_COMPLETE_EMAIL_HTML appropriately:

        ``registration/admin_approve_complete_email_subject.txt``
            This template will be used for the subject line of the
            email. Because it is used as the subject line of an email,
            this template's output **must** be only a single line of
            text; output longer than one line will be forcibly joined
            into only a single line.

        ``registration/admin_approve_complete_email.txt``
            This template will be used for the text body of the email.

        ``registration/admin_approve_complete_email.html``
            This template will be used for the text body of the email.

        These templates will each receive the following context
        variables:

        ``user``
            The new user account

        ``site``
            An object representing the site on which the user
            registered; depending on whether ``django.contrib.sites``
            is installed, this may be an instance of either
            ``django.contrib.sites.models.Site`` (if the sites
            application is installed) or
            ``django.contrib.sites.requests.RequestSite`` (if
            not). Consult the documentation for the Django sites
            framework for details regarding these objects' interfaces.

        ``request``
            Optional Django's ``HttpRequest`` object from view.
            If supplied will be passed to the template for better
            flexibility via ``RequestContext``.
        """
        admin_approve_complete_email_subject = getattr(
            settings, 'APPROVAL_COMPLETE_EMAIL_SUBJECT',
            'registration/admin_approve_complete_email_subject.txt')
        admin_approve_complete_email_body = getattr(
            settings, 'APPROVAL_COMPLETE_EMAIL_BODY',
            'registration/admin_approve_complete_email.txt')
        admin_approve_complete_email_html = getattr(
            settings, 'APPROVAL_COMPLETE_EMAIL_HTML',
            'registration/admin_approve_complete_email.html')

        ctx_dict = {
            'user': self.user.get_username(),
            'site': site,
        }
        send_email(
            [self.user.email], ctx_dict,
            admin_approve_complete_email_subject,
            admin_approve_complete_email_body,
            admin_approve_complete_email_html
        )
