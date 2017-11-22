from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Update the docs then reindex them in the search vector field.
    """
    def handle(self, **options):
        call_command('update_docs', update_index=True, **options)
