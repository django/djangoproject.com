from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Update the docs then reindex them in elasticsearch.
    """
    def handle(self, **options):
        call_command('update_docs', **options)
        call_command('update_index', **options)
