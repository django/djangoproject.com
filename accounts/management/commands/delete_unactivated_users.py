"""Delete unactivated user accounts.

An alternative to django-registration-redux's ``cleanupregistration`` with:

* **Bulk deletion** - single ``QuerySet.delete()`` instead of iterating one by
  one. Django still batches the SQL statements via ``GET_ITERATOR_CHUNK_SIZE``,
  but the number of queries does not grow per user.
* **Hard safety** - users with protected related objects (BoardMember,
  Releaser) are skipped, so a single protected user cannot block the cleanup.
* **``--dry-run``** for a safe preview.
"""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = (
        "Delete users and profiles that never activated their account "
        "(older than ACCOUNT_ACTIVATION_DAYS and never clicked the activation link). "
        "Only User, Profile, and RegistrationProfile rows are removed. Users with "
        "protected related objects (e.g. BoardMember or Releaser) are skipped."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting.",
        )

    def handle(self, *args, **options):
        verbosity = options["verbosity"]
        dry_run = options["dry_run"]

        expiry_cutoff = timezone.now() - timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS
        )

        qs = User.objects.filter(
            is_active=False,
            date_joined__lt=expiry_cutoff,
            registrationprofile__activated=False,
            last_login__isnull=True,
            # Skip users holding data that must outlive them. Deleting in bulk
            # is all or nothing, so a single protected user would otherwise
            # abort the whole run.
            boardmember__isnull=True,
            releaser__isnull=True,
        )
        total = qs.count()

        if verbosity >= 1:
            self.stdout.write(f"Found {total} unactivated user(s) to process.")

        if total == 0:
            if verbosity >= 1:
                self.stdout.write("Nothing to do.")
            return

        if dry_run:
            if verbosity >= 1:
                self.stdout.write(
                    self.style.NOTICE(
                        f"DRY RUN - would delete {total} user(s) "
                        f"(cascading to Profile and RegistrationProfile)."
                    )
                )
            return

        # CASCADE chain: User -> Profile, User -> RegistrationProfile.
        with transaction.atomic():
            _deleted_count, deleted_by_model = qs.delete()

        if verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {deleted_by_model.get('auth.User', 0)} user(s) "
                    f"(plus associated profiles)."
                )
            )
