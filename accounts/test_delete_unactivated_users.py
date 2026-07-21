from datetime import timedelta
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from registration.models import RegistrationProfile

from accounts.models import Profile
from checklists.models import Releaser
from foundation.models import Banner, BoardMember, Office, Term


class DeleteUnactivatedUsersTests(TestCase):
    def make_user(self, days_ago=4, activated=False, **userkwargs):
        prefix = "activated" if activated else "user"
        userkwargs.setdefault("username", f"{prefix}-{days_ago}")
        userkwargs.setdefault("email", f"{prefix}-{days_ago}@example.com")
        user = User.objects.create_user(
            password="password", is_active=activated, **userkwargs
        )
        user.date_joined = timezone.now() - timedelta(days=days_ago)
        user.save()
        RegistrationProfile.objects.create(
            user=user,
            activation_key="abc123",
            activated=activated,
        )
        Profile.objects.create(user=user)
        return user

    def make_board_member(self, user):
        return BoardMember.objects.create(
            account=user,
            office=Office.objects.create(name="Chair"),
            term=Term.objects.create(year=2024),
        )

    def make_releaser(self, user):
        return Releaser.objects.create(
            user=user,
            key_id="ABC123",
            key_url="https://example.com/key.asc",
        )

    def test_deletes_expired_unactivated_user(self):
        user = self.make_user(days_ago=4)

        call_command("delete_unactivated_users", verbosity=0)

        self.assertFalse(User.objects.filter(pk=user.pk).exists())
        self.assertFalse(Profile.objects.filter(user_id=user.pk).exists())

    def test_no_one_query_per_user_deleted(self):
        self.make_user(days_ago=4)
        with CaptureQueriesContext(connection) as one_user:
            call_command("delete_unactivated_users", verbosity=0)
        self.assertEqual(User.objects.count(), 0)

        for days_ago in (5, 6, 7):
            self.make_user(days_ago=days_ago)
        with CaptureQueriesContext(connection) as three_users:
            call_command("delete_unactivated_users", verbosity=0)
        self.assertEqual(User.objects.count(), 0)

        # Django batches deletions, so the count is not constant for an
        # arbitrarily large backlog, but it must not grow once per user.
        self.assertEqual(len(three_users), len(one_user))

    def test_no_unactivated_users(self):
        self.make_user(days_ago=4, activated=True)

        call_command("delete_unactivated_users", verbosity=0)

        self.assertEqual(User.objects.count(), 1)

    def test_recently_registered_not_deleted(self):
        user = self.make_user(days_ago=1)

        call_command("delete_unactivated_users", verbosity=0)

        self.assertTrue(User.objects.filter(pk=user.pk).exists())

    def test_activated_user_not_deleted(self):
        user = self.make_user(days_ago=30, activated=True)

        call_command("delete_unactivated_users", verbosity=0)

        self.assertTrue(User.objects.filter(pk=user.pk).exists())

    def test_logged_in_user_not_deleted(self):
        user = self.make_user(days_ago=4)
        user.last_login = timezone.now() - timedelta(days=3)
        user.save()

        call_command("delete_unactivated_users", verbosity=0)

        self.assertTrue(User.objects.filter(pk=user.pk).exists())

    @override_settings(ACCOUNT_ACTIVATION_DAYS=7)
    def test_respects_custom_activation_days(self):
        user = self.make_user(days_ago=6)

        call_command("delete_unactivated_users", verbosity=0)

        self.assertTrue(User.objects.filter(pk=user.pk).exists())

    def test_board_member_skipped(self):
        user = self.make_user(days_ago=4)
        self.make_board_member(user)

        call_command("delete_unactivated_users", verbosity=0)

        self.assertTrue(User.objects.filter(pk=user.pk).exists())

    def test_releaser_skipped(self):
        user = self.make_user(days_ago=4)
        self.make_releaser(user)

        call_command("delete_unactivated_users", verbosity=0)

        self.assertTrue(User.objects.filter(pk=user.pk).exists())

    def test_both_board_member_and_releaser_skipped(self):
        user = self.make_user(days_ago=4)
        self.make_board_member(user)
        self.make_releaser(user)

        call_command("delete_unactivated_users", verbosity=0)

        self.assertTrue(User.objects.filter(pk=user.pk).exists())

    def test_protected_user_does_not_block_the_others(self):
        protected = self.make_user(days_ago=4, username="protected")
        self.make_releaser(protected)
        deletable = self.make_user(days_ago=5, username="deletable")

        call_command("delete_unactivated_users", verbosity=0)

        self.assertTrue(User.objects.filter(pk=protected.pk).exists())
        self.assertFalse(User.objects.filter(pk=deletable.pk).exists())

    def test_allows_banner_set_null(self):
        user = self.make_user(days_ago=4)
        banner = Banner.objects.create(title="Test Banner", created_by=user)

        call_command("delete_unactivated_users", verbosity=0)

        self.assertFalse(User.objects.filter(pk=user.pk).exists())
        banner.refresh_from_db()
        self.assertIsNone(banner.created_by)

    def test_dry_run_does_not_delete(self):
        user = self.make_user(days_ago=4)

        call_command("delete_unactivated_users", "--dry-run", verbosity=0)

        self.assertTrue(User.objects.filter(pk=user.pk).exists())

    def test_verbosity_output(self):
        self.make_user(days_ago=4)
        self.make_user(days_ago=5)

        out = StringIO()
        call_command("delete_unactivated_users", verbosity=1, stdout=out)

        self.assertIn("Deleted 2 user(s)", out.getvalue())

    def test_empty_database(self):
        call_command("delete_unactivated_users", verbosity=0)
        self.assertEqual(User.objects.count(), 0)

    def test_user_without_profile(self):
        user = User.objects.create_user(
            username="no-profile",
            email="no-profile@example.com",
            password="password",
            is_active=False,
        )
        user.date_joined = timezone.now() - timedelta(days=4)
        user.save()
        RegistrationProfile.objects.create(
            user=user, activation_key="abc", activated=False
        )

        call_command("delete_unactivated_users", verbosity=0)

        self.assertFalse(User.objects.filter(pk=user.pk).exists())

    def test_user_without_registration_profile(self):
        user = User.objects.create_user(
            username="direct",
            email="direct@example.com",
            password="password",
            is_active=False,
        )
        user.date_joined = timezone.now() - timedelta(days=30)
        user.save()
        Profile.objects.create(user=user)

        call_command("delete_unactivated_users", verbosity=0)

        self.assertTrue(User.objects.filter(pk=user.pk).exists())
