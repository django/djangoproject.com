"""
A management command which deletes expired accounts (e.g.,
accounts which signed up but never activated) from the database.

Calls ``RegistrationProfile.objects.delete_expired_users()``, which
contains the actual logic for determining which accounts are deleted.

"""

from django.core.management.base import BaseCommand

from ...models import RegistrationProfile


class Command(BaseCommand):
    help = "Delete expired user registrations from the database"

    def handle(self, *args, **options):
        self.stdout.write('Running cleanupregistration.')
        deleted_count = RegistrationProfile.objects.delete_expired_users()
        if deleted_count == 0:
            self.stdout.write('cleanupregistration completed. There is no user that has to be deleted.')
        else:
            self.stdout.write('cleanupregistration completed. Deleted user count=%d' % deleted_count)
