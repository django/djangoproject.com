import datetime
import hashlib
import random
import re
import string
import warnings
from copy import copy
from datetime import timedelta

from django.apps import apps
from django.conf import settings
from django.core import mail
from django.core import management
from django.core.exceptions import ImproperlyConfigured
from django.test import TransactionTestCase
from django.test import override_settings
from django.utils.crypto import get_random_string
from django.utils.timezone import now as datetime_now

from registration.models import RegistrationProfile
from registration.models import SupervisedRegistrationProfile
from registration.users import UserModel

Site = apps.get_model('sites', 'Site')


@override_settings(ACCOUNT_ACTIVATION_DAYS=7,
                   REGISTRATION_DEFAULT_FROM_EMAIL='registration@email.com',
                   REGISTRATION_EMAIL_HTML=True,
                   DEFAULT_FROM_EMAIL='django@email.com')
class RegistrationModelTests(TransactionTestCase):
    """
    Test the model and manager used in the default backend.

    """
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    registration_profile = RegistrationProfile

    def setUp(self):
        warnings.simplefilter('always', UserWarning)

    def test_profile_creation(self):
        """
        Creating a registration profile for a user populates the
        profile with the correct user and a SHA256 hash to use as
        activation key.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)

        self.assertEqual(self.registration_profile.objects.count(), 1)
        self.assertEqual(profile.user.id, new_user.id)
        self.assertTrue(re.match('^[a-f0-9]{40,64}$', profile.activation_key))
        self.assertEqual(str(profile),
                         "Registration information for alice")

    def test_activation_email(self):
        """
        ``RegistrationProfile.send_activation_email`` sends an
        email.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.send_activation_email(Site.objects.get_current())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])

    @override_settings(ACTIVATION_EMAIL_HTML='does-not-exist')
    def test_activation_email_missing_template(self):
        """
        ``RegistrationProfile.send_activation_email`` sends an
        email.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.send_activation_email(Site.objects.get_current())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])

    def test_activation_email_uses_registration_default_from_email(self):
        """
        ``RegistrationProfile.send_activation_email`` sends an
        email.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.send_activation_email(Site.objects.get_current())
        self.assertEqual(mail.outbox[0].from_email, 'registration@email.com')

    @override_settings(REGISTRATION_DEFAULT_FROM_EMAIL=None)
    def test_activation_email_falls_back_to_django_default_from_email(self):
        """
        ``RegistrationProfile.send_activation_email`` sends an
        email.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.send_activation_email(Site.objects.get_current())
        self.assertEqual(mail.outbox[0].from_email, 'django@email.com')

    @override_settings(REGISTRATION_USE_SITE_EMAIL=True,
                       REGISTRATION_SITE_USER_EMAIL='admin')
    def test_activation_email_uses_site_address(self):
        """
        ``RegistrationProfile.send_activation_email`` sends an
        email with the ``from`` address configured by the site.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        site = Site.objects.get_current()
        profile.send_activation_email(site)
        from_email = 'admin@{}'.format(site.domain)
        self.assertEqual(mail.outbox[0].from_email, from_email)

    @override_settings(REGISTRATION_USE_SITE_EMAIL=True)
    def test_activation_email_uses_site_address_improperly_configured(self):
        """
        ``RegistrationProfile.send_activation_email`` won't send an email if
        improperly configured.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        with self.assertRaises(ImproperlyConfigured):
            profile.send_activation_email(Site.objects.get_current())

    def test_activation_email_is_html_by_default(self):
        """
        ``RegistrationProfile.send_activation_email`` sends an html
        email by default.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.send_activation_email(Site.objects.get_current())

        self.assertEqual(len(mail.outbox[0].alternatives), 1)

    @override_settings(REGISTRATION_EMAIL_HTML=False)
    def test_activation_email_is_plain_text_if_html_disabled(self):
        """
        ``RegistrationProfile.send_activation_email`` sends a plain
        text email if settings.REGISTRATION_EMAIL_HTML is False.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.send_activation_email(Site.objects.get_current())

        self.assertEqual(len(mail.outbox[0].alternatives), 0)

    def test_user_creation(self):
        """
        Creating a new user populates the correct data, and sets the
        user's account inactive.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        self.assertEqual(new_user.get_username(), 'alice')
        self.assertEqual(new_user.email, 'alice@example.com')
        self.assertTrue(new_user.check_password('swordfish'))
        self.assertFalse(new_user.is_active)

        expiration_date = datetime_now() - timedelta(
            settings.ACCOUNT_ACTIVATION_DAYS
        )
        self.assertGreater(new_user.date_joined, expiration_date)

    def test_user_creation_email(self):
        """
        By default, creating a new user sends an activation email.

        """
        self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        self.assertEqual(len(mail.outbox), 1)

    def test_user_creation_no_email(self):
        """
        Passing ``send_email=False`` when creating a new user will not
        send an activation email.

        """
        self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(),
            send_email=False, **self.user_info)
        self.assertEqual(len(mail.outbox), 0)

    def test_user_creation_old_date_joined(self):
        """
        If ``user.date_joined`` is well in the past, ensure that we reset it.
        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        self.assertEqual(new_user.get_username(), 'alice')
        self.assertEqual(new_user.email, 'alice@example.com')
        self.assertTrue(new_user.check_password('swordfish'))
        self.assertFalse(new_user.is_active)

        expiry_date = datetime_now() - timedelta(settings.ACCOUNT_ACTIVATION_DAYS)
        self.assertGreater(new_user.date_joined, expiry_date)

    def test_unexpired_account_old_date_joined(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``False`` within
        the activation window. Even if the user was created in the past.

        """
        self.user_info['date_joined'] = datetime_now(
        ) - timedelta(settings.ACCOUNT_ACTIVATION_DAYS + 1)
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        self.assertFalse(profile.activation_key_expired())

    def test_unexpired_account(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``False``
        within the activation window.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        self.assertFalse(profile.activation_key_expired())

    def test_active_account_activation_key_expired(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``True``
        when the account is already active.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())
        profile.refresh_from_db()
        self.assertTrue(profile.activation_key_expired())

    def test_active_account_and_expired_accountactivation_key_expired(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``True``
        when the account is already active and the activation window has passed.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        new_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        new_user.save()
        profile = self.registration_profile.objects.get(user=new_user)
        self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())
        profile.refresh_from_db()
        self.assertTrue(profile.activation_key_expired())

    def test_expired_account(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``True``
        outside the activation window.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        new_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        new_user.save()
        profile = self.registration_profile.objects.get(user=new_user)
        self.assertTrue(profile.activation_key_expired())

    def test_valid_activation(self):
        """
        Activating a user within the permitted window makes the
        account active, and resets the activation key.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())

        self.assertIsInstance(user, UserModel())
        self.assertEqual(user.id, new_user.id)
        self.assertTrue(user.is_active)
        self.assertTrue(activated)

        profile = self.registration_profile.objects.get(user=new_user)
        self.assertTrue(profile.activated)

    def test_valid_activation_with_profile(self):
        """
        Activating a user within the permitted window makes the
        account active, and resets the activation key.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        profile, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current(), get_profile=True)

        self.assertIsInstance(profile, self.registration_profile)
        self.assertEqual(profile.id, profile.id)
        self.assertTrue(profile.activated)
        self.assertTrue(activated)

        new_user.refresh_from_db()
        self.assertTrue(profile.user.id, new_user.id)
        self.assertTrue(new_user.is_active)

    def test_expired_activation(self):
        """
        Attempting to activate outside the permitted window does not
        activate the account.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        new_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        new_user.save()

        profile = self.registration_profile.objects.get(user=new_user)
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())

        self.assertIs(user, False)
        self.assertFalse(activated)

        new_user = UserModel().objects.get(username='alice')
        self.assertFalse(new_user.is_active)

        profile = self.registration_profile.objects.get(user=new_user)
        self.assertFalse(profile.activated)

    def test_activation_invalid_key(self):
        """
        Attempting to activate with a key which is not a SHA256 hash
        fails.

        """
        user, activated = self.registration_profile.objects.activate_user(
            'foo', Site.objects.get_current())
        self.assertIs(user, False)
        self.assertFalse(activated)

    def test_activation_already_activated(self):
        """
        Attempting to re-activate an already-activated account fails.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())

        profile = self.registration_profile.objects.get(user=new_user)
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())
        self.assertEqual(user, new_user)
        self.assertFalse(activated)

    def test_activation_deactivated(self):
        """
        Attempting to re-activate a deactivated account fails.
        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())

        # Deactivate the new user.
        new_user.is_active = False
        new_user.save()

        # Try to activate again and ensure False is returned.
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())
        self.assertFalse(activated)

    def test_activation_nonexistent_key(self):
        """
        Attempting to activate with a non-existent key (i.e., one not
        associated with any account) fails.

        """
        # Due to the way activation keys are constructed during
        # registration, this will never be a valid key.
        invalid_key = hashlib.sha256('foo'.encode('latin-1')).hexdigest()
        _, activated = self.registration_profile.objects.activate_user(
            invalid_key, Site.objects.get_current())
        self.assertFalse(activated)

    def test_expired_user_deletion_activation_window(self):
        """
        ``RegistrationProfile.objects.delete_expired_users()`` only
        deletes inactive users whose activation window has expired.

        """
        self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        expired_user = (self.registration_profile.objects
                        .create_inactive_user(
                            site=Site.objects.get_current(),
                            username='bob',
                            password='secret',
                            email='bob@example.com'))
        expired_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        expired_user.save()

        deleted_count = self.registration_profile.objects.delete_expired_users()
        self.assertEqual(deleted_count, 1)
        self.assertEqual(self.registration_profile.objects.count(), 1)
        self.assertRaises(UserModel().DoesNotExist,
                          UserModel().objects.get, username='bob')

    def test_expired_user_deletion_ignore_activated(self):
        """
        ``RegistrationProfile.objects.delete_expired_users()`` only
        deletes inactive users whose activation window has expired and if
        their profile is not activated.

        """
        user = (self.registration_profile.objects
                .create_inactive_user(
                    site=Site.objects.get_current(),
                    username='bob',
                    password='secret',
                    email='bob@example.com'))
        profile = self.registration_profile.objects.get(user=user)
        _, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())
        self.assertTrue(activated)
        # Expire the activation window.
        user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        user.save()

        deleted_count = self.registration_profile.objects.delete_expired_users()
        self.assertEqual(deleted_count, 0)
        self.assertEqual(self.registration_profile.objects.count(), 1)
        self.assertEqual(UserModel().objects.get(username='bob'), user)

    def test_expired_user_deletion_missing_user(self):
        """
        ``RegistrationProfile.objects.delete_expired_users()`` only deletes
        inactive users whose activation window has expired. If a ``UserModel``
        is not present, the delete continues gracefully.

        """
        self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        expired_user = (self.registration_profile.objects
                        .create_inactive_user(
                            site=Site.objects.get_current(),
                            username='bob',
                            password='secret',
                            email='bob@example.com'))
        expired_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        expired_user.save()
        # Ensure that we cleanup the expired profile even if the user does not
        # exist. We simulate this with raw SQL, calling `expired_user.delete()`
        # would result in the profile being deleted on cascade.
        UserModel().objects.raw('DELETE FROM users WHERE username="bob"')

        deleted_count = self.registration_profile.objects.delete_expired_users()
        self.assertEqual(deleted_count, 1)
        self.assertEqual(self.registration_profile.objects.count(), 1)
        self.assertRaises(UserModel().DoesNotExist,
                          UserModel().objects.get, username='bob')

    def test_manually_registered_account(self):
        """
        Test if a user failed to go through the registration flow but was
        manually marked ``is_active`` in the DB.  Although the profile is
        expired and not active, we should never delete active users.
        """
        active_user = (self.registration_profile.objects
                       .create_inactive_user(
                           site=Site.objects.get_current(),
                           username='bob',
                           password='secret',
                           email='bob@example.com'))
        active_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        active_user.is_active = True
        active_user.save()

        deleted_count = self.registration_profile.objects.delete_expired_users()
        self.assertEqual(deleted_count, 0)
        self.assertEqual(self.registration_profile.objects.count(), 1)
        self.assertEqual(UserModel().objects.get(username='bob'), active_user)

    def test_management_command(self):
        """
        The ``cleanupregistration`` management command properly
        deletes expired accounts.

        """
        self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        expired_user = (self.registration_profile.objects
                        .create_inactive_user(site=Site.objects.get_current(),
                                              username='bob',
                                              password='secret',
                                              email='bob@example.com'))
        expired_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        expired_user.save()

        management.call_command('cleanupregistration')
        self.assertEqual(self.registration_profile.objects.count(), 1)
        self.assertRaises(UserModel().DoesNotExist,
                          UserModel().objects.get, username='bob')

    def test_resend_activation_email(self):
        """
        Test resending activation email to an existing user
        """
        user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), send_email=False, **self.user_info)
        self.assertEqual(len(mail.outbox), 0)

        profile = self.registration_profile.objects.get(user=user)
        orig_activation_key = profile.activation_key

        self.assertTrue(self.registration_profile.objects.resend_activation_mail(
            email=self.user_info['email'],
            site=Site.objects.get_current(),
        ))

        profile = self.registration_profile.objects.get(pk=profile.pk)
        new_activation_key = profile.activation_key

        self.assertNotEqual(orig_activation_key, new_activation_key)
        self.assertEqual(len(mail.outbox), 1)

    def test_resend_activation_email_nonexistent_user(self):
        """
        Test resending activation email to a nonexisting user
        """
        self.assertFalse(self.registration_profile.objects.resend_activation_mail(
            email=self.user_info['email'],
            site=Site.objects.get_current(),
        ))
        self.assertEqual(len(mail.outbox), 0)

    def test_resend_activation_email_activated_user(self):
        """
        Test the scenario where user tries to resend activation code
        to the already activated user's email
        """
        user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), send_email=False, **self.user_info)

        profile = self.registration_profile.objects.get(user=user)
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())
        self.assertTrue(user.is_active)
        self.assertTrue(activated)

        self.assertFalse(self.registration_profile.objects.resend_activation_mail(
            email=self.user_info['email'],
            site=Site.objects.get_current(),
        ))
        self.assertEqual(len(mail.outbox), 0)

    def test_resend_activation_email_expired_user(self):
        """
        Test the scenario where user tries to resend activation code
        to the expired user's email
        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), send_email=False, **self.user_info)
        new_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        new_user.save()

        profile = self.registration_profile.objects.get(user=new_user)
        self.assertTrue(profile.activation_key_expired())

        self.assertFalse(self.registration_profile.objects.resend_activation_mail(
            email=self.user_info['email'],
            site=Site.objects.get_current(),
        ))
        self.assertEqual(len(mail.outbox), 0)

    def test_resend_activation_email_nonunique_email(self):
        """
        Test the scenario where user tries to resend activation code
        to the expired user's email
        """
        user1 = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), send_email=False, **self.user_info)
        user2_info = copy(self.user_info)
        user2_info['username'] = 'bob'
        user2 = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), send_email=False, **user2_info)
        self.assertEqual(user1.email, user2.email)
        self.assertFalse(self.registration_profile.objects.resend_activation_mail(
            email=self.user_info['email'],
            site=Site.objects.get_current(),
        ))
        self.assertEqual(len(mail.outbox), 0)

    def test_activation_key_backwards_compatibility(self):
        """
        Make sure that users created with the old create_new_activation_key
        method can still be activated.
        """
        current_method = self.registration_profile.create_new_activation_key

        def old_method(self, save=True):
            salt = hashlib.sha1(
                str(random.random()).encode('ascii')
            ).hexdigest()[:5]
            salt = salt.encode('ascii')
            user_pk = str(self.user.pk)
            if isinstance(user_pk, str):
                user_pk = user_pk.encode()
            self.activation_key = hashlib.sha1(salt + user_pk).hexdigest()
            if save:
                self.save()
            return self.activation_key

        self.registration_profile.create_new_activation_key = old_method

        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)

        self.registration_profile.create_new_activation_key = current_method
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())

        self.assertIsInstance(user, UserModel())
        self.assertEqual(user.id, new_user.id)
        self.assertTrue(user.is_active)
        self.assertTrue(activated)

        profile = self.registration_profile.objects.get(user=new_user)
        self.assertTrue(profile.activated)

    def test_activation_key_backwards_compatibility_sha1(self):
        """
        Make sure that users created with the old create_new_activation_key
        method can still be activated.
        """
        current_method = self.registration_profile.create_new_activation_key

        def old_method(self, save=True):
            random_string = get_random_string(length=32, allowed_chars=string.printable)
            self.activation_key = hashlib.sha1(random_string.encode()).hexdigest()
            if save:
                self.save()
            return self.activation_key

        self.registration_profile.create_new_activation_key = old_method

        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)

        self.registration_profile.create_new_activation_key = current_method
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())

        self.assertIsInstance(user, UserModel())
        self.assertEqual(user.id, new_user.id)
        self.assertTrue(user.is_active)
        self.assertTrue(activated)

        profile = self.registration_profile.objects.get(user=new_user)
        self.assertTrue(profile.activated)


@override_settings(
    ADMINS=(
        ('T-Rex', 'admin1@iamtrex.com'),
        ('Flea', 'admin2@iamaflea.com')
    )
)
class SupervisedRegistrationModelTests(RegistrationModelTests):
    """
    Test the model and manager used in the admin_approval backend.

    """

    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    registration_profile = SupervisedRegistrationProfile

    def test_valid_activation(self):
        """
        Activating a user within the permitted window makes the
        account active, and resets the activation key.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())

        self.assertIsInstance(user, UserModel())
        self.assertEqual(user.id, new_user.id)
        self.assertFalse(user.is_active)
        self.assertTrue(activated)

        profile = self.registration_profile.objects.get(user=new_user)
        self.assertTrue(profile.activated)

    def test_valid_activation_with_profile(self):
        """
        Activating a user within the permitted window makes the
        account active, and resets the activation key.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        profile, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current(), get_profile=True)

        self.assertIsInstance(profile, self.registration_profile)
        self.assertEqual(profile.id, profile.id)
        self.assertTrue(profile.activated)
        self.assertTrue(activated)

        new_user.refresh_from_db()
        self.assertTrue(profile.user.id, new_user.id)
        self.assertFalse(new_user.is_active)

    def test_resend_activation_email_activated_user(self):
        """
        Test the scenario where user tries to resend activation code
        to the already activated user's email
        """
        user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), send_email=False, **self.user_info)

        profile = self.registration_profile.objects.get(user=user)
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())
        self.assertFalse(user.is_active)
        self.assertTrue(activated)

        self.assertFalse(self.registration_profile.objects.resend_activation_mail(
            email=self.user_info['email'],
            site=Site.objects.get_current(),
        ))
        # Outbox has one mail, admin approve mail

        self.assertEqual(len(mail.outbox), 1)
        admins_emails = [value[1] for value in settings.REGISTRATION_ADMINS]
        for email in mail.outbox[0].to:
            self.assertIn(email, admins_emails)

    def test_admin_approval_email(self):
        """
        ``SupervisedRegistrationManager.send_admin_approve_email`` sends an
        email to the site administrators

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.activated = True
        self.registration_profile.objects.send_admin_approve_email(
            new_user, Site.objects.get_current())
        self.assertEqual(len(mail.outbox), 1)
        admins_emails = [value[1] for value in settings.REGISTRATION_ADMINS]
        for email in mail.outbox[0].to:
            self.assertIn(email, admins_emails)

    def test_admin_approval_email_uses_registration_default_from_email(self):
        """
        ``SupervisedRegistrationManager.send_admin_approve_email``` sends an
        email.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.activated = True
        self.registration_profile.objects.send_admin_approve_email(
            new_user, Site.objects.get_current())
        self.assertEqual(mail.outbox[0].from_email, 'registration@email.com')

    @override_settings(REGISTRATION_DEFAULT_FROM_EMAIL=None)
    def test_admin_approval_email_falls_back_to_django_default_from_email(self):
        """
        ``SupervisedRegistrationManager.send_admin_approve_email`` sends an
        email.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.activated = True
        self.registration_profile.objects.send_admin_approve_email(
            new_user, Site.objects.get_current())
        self.assertEqual(mail.outbox[0].from_email, 'django@email.com')

    def test_admin_approval_email_is_html_by_default(self):
        """
        ``SupervisedRegistrationProfile.send_activation_email`` sends an html
        email by default.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.activated = True
        self.registration_profile.objects.send_admin_approve_email(
            new_user, Site.objects.get_current())

        self.assertEqual(len(mail.outbox[0].alternatives), 1)

    @override_settings(REGISTRATION_EMAIL_HTML=False)
    def test_admin_approval_email_is_plain_text_if_html_disabled(self):
        """
        ``SupervisedRegistrationProfile.send_activation_email`` sends a plain
        text email if settings.REGISTRATION_EMAIL_HTML is False.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.activated = True
        self.registration_profile.objects.send_admin_approve_email(
            new_user, Site.objects.get_current())

        self.assertEqual(len(mail.outbox[0].alternatives), 0)

    def test_active_account_activation_key_expired(self):
        """
        ``SupervisedRegistrationProfile.activation_key_expired()`` is ``True``
        when the account is already active.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())
        self.registration_profile.objects.admin_approve_user(
            profile.id, Site.objects.get_current())
        profile.refresh_from_db()
        self.assertTrue(profile.activation_key_expired())

    def test_active_account_and_expired_accountactivation_key_expired(self):
        """
        ``SupervisedRegistrationProfile.activation_key_expired()`` is ``True``
        when the account is already active and the activation window has passed.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        new_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        new_user.save()
        profile = self.registration_profile.objects.get(user=new_user)
        self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())
        self.registration_profile.objects.admin_approve_user(
            profile.id, Site.objects.get_current())
        profile.refresh_from_db()
        self.assertTrue(profile.activation_key_expired())

    def test_admin_approval_complete_email(self):
        """
        ``SupervisedRegistrationManager.send_admin_approve_complete_email``
        sends an email to the approved user

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.send_admin_approve_complete_email(Site.objects.get_current())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])

    def test_admin_approval_complete_email_uses_registration_default_from_email(self):
        """
        ``SupervisedRegistrationManager.send_admin_approve_complete_email``
        sends an email

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.send_admin_approve_complete_email(Site.objects.get_current())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, 'registration@email.com')

    @override_settings(REGISTRATION_DEFAULT_FROM_EMAIL=None)
    def test_admin_approval_complete_email_falls_back_to_django_default_from_email(self):
        """
        ``SupervisedRegistrationManager.send_admin_approve_complete_email``
        sends an email

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.send_admin_approve_complete_email(Site.objects.get_current())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, 'django@email.com')

    def test_admin_approval_complete_email_is_html_by_default(self):
        """
        ``SupervisedRegistrationProfile.send_admin_approve_complete_email``
        sends an html email by default.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.send_admin_approve_complete_email(Site.objects.get_current())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].alternatives), 1)

    @override_settings(REGISTRATION_EMAIL_HTML=False)
    def test_admin_approval_complete_email_is_plain_text_if_html_disabled(self):
        """
        ``SupervisedRegistrationProfile.send_admin_approve_complete_email``
        sends a plain text email if settings.REGISTRATION_EMAIL_HTML is False.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = self.registration_profile.objects.create_profile(new_user)
        profile.send_admin_approve_complete_email(Site.objects.get_current())
        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(len(mail.outbox[0].alternatives), 0)

    def test_valid_admin_approval(self):
        """
        Approving an already activated user's account makes the user
        active
        """

        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())

        self.assertIsInstance(user, UserModel())

        user = self.registration_profile.objects.admin_approve_user(
            profile.id, Site.objects.get_current())
        self.assertIsInstance(user, UserModel())
        self.assertIs(user.is_active, True)

    def test_admin_approval_not_activated(self):
        """
        Approving a non activated user's account fails
        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)

        user = self.registration_profile.objects.admin_approve_user(
            profile.id, Site.objects.get_current())
        self.assertIs(user, False)
        self.assertIs(profile.user.is_active, False)

    def test_admin_approval_already_approved(self):
        """
        Approving an already approved user's account returns the User model
        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())

        self.assertIsInstance(user, UserModel())
        self.assertTrue(activated)

        user = self.registration_profile.objects.admin_approve_user(
            profile.id, Site.objects.get_current())
        self.assertIsInstance(user, UserModel())
        self.assertIs(user.is_active, True)

    def test_admin_approval_nonexistent_id(self):
        """
        Approving a non existent user profile does nothing and returns False
        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)

        user = self.registration_profile.objects.admin_approve_user(
            profile.id, Site.objects.get_current())
        self.assertIs(user, False)

    def test_activation_already_activated(self):
        """
        Attempting to re-activate an already-activated account fails.

        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)
        self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())

        profile = self.registration_profile.objects.get(user=new_user)
        _, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())
        self.assertFalse(activated)

    def test_activation_key_backwards_compatibility(self):
        """
        Make sure that users created with the old create_new_activation_key
        method can still be activated.
        """
        current_method = self.registration_profile.create_new_activation_key

        def old_method(self, save=True):
            salt = hashlib.sha1(
                str(random.random()).encode('ascii')
            ).hexdigest()[:5]
            salt = salt.encode('ascii')
            user_pk = str(self.user.pk)
            if isinstance(user_pk, str):
                user_pk = user_pk.encode()
            self.activation_key = hashlib.sha1(salt + user_pk).hexdigest()
            if save:
                self.save()
            return self.activation_key

        self.registration_profile.create_new_activation_key = old_method

        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)

        self.registration_profile.create_new_activation_key = current_method
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())

        self.assertIsInstance(user, UserModel())
        self.assertEqual(user.id, new_user.id)
        self.assertFalse(user.is_active)
        self.assertTrue(activated)

        profile = self.registration_profile.objects.get(user=new_user)
        self.assertTrue(profile.activated)

    def test_activation_key_backwards_compatibility_sha1(self):
        """
        Make sure that users created with the old create_new_activation_key
        method can still be activated.
        """
        current_method = self.registration_profile.create_new_activation_key

        def old_method(self, save=True):
            random_string = get_random_string(length=32, allowed_chars=string.printable)
            self.activation_key = hashlib.sha1(random_string.encode()).hexdigest()
            if save:
                self.save()
            return self.activation_key

        self.registration_profile.create_new_activation_key = old_method

        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)
        profile = self.registration_profile.objects.get(user=new_user)

        self.registration_profile.create_new_activation_key = current_method
        user, activated = self.registration_profile.objects.activate_user(
            profile.activation_key, Site.objects.get_current())

        self.assertIsInstance(user, UserModel())
        self.assertEqual(user.id, new_user.id)
        self.assertFalse(user.is_active)
        self.assertTrue(activated)

        profile = self.registration_profile.objects.get(user=new_user)
        self.assertTrue(profile.activated)

    @override_settings(ADMINS=(), REGISTRATION_ADMINS=())
    def test_no_admins_registered(self):
        """
        Approving a non existent user profile does nothing and returns False
        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)

        with self.assertRaises(ImproperlyConfigured):
            self.registration_profile.objects.send_admin_approve_email(
                new_user, Site.objects.get_current())

    @override_settings(REGISTRATION_ADMINS=())
    def test_no_registration_admins_registered(self):
        """
        Approving a non existent user profile does nothing and returns False
        """
        new_user = self.registration_profile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)

        with warnings.catch_warnings(record=True) as _warning:
            self.registration_profile.objects.send_admin_approve_email(
                new_user, Site.objects.get_current())

            assertion_error = '''No warning triggered for unregistered
             REGISTRATION_ADMINS'''
            self.assertTrue(len(_warning) > 0, assertion_error)
            self.assertTrue('REGISTRATION_ADMINS' in str(_warning[-1].message),
                            assertion_error)
