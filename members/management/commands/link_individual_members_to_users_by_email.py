from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import IndividualMember


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--no-logging",
            action="store_true",
            help="Disable writing number of updated records to stdout.",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            count = IndividualMember.match_and_set_users_by_email()
        if not options["no_logging"]:
            self.stdout.write(f"Updated: {count}")
