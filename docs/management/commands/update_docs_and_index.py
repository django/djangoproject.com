from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Update the docs then reindex them in the search vector field.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help=(
                "Force docs update even if docs in git didn't change or the "
                "version is no longer supported."
            ),
        )

    def handle(self, **options):
        call_command("update_docs", update_index=True, **options)
