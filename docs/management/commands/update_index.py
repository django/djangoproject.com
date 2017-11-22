from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Document
from ...search import DOCUMENT_SEARCH_VECTOR


class Command(BaseCommand):

    def log(self, msg, level=2):
        """
        Small log helper
        """
        if self.verbosity >= level:
            self.stdout.write(msg)

    @transaction.atomic
    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        Document.objects.update(search=None)
        updated = (
            # Don't index the module pages since source code is hard to
            # combine with full text search.
            Document.objects.exclude(path__startswith='_modules')
            # Not the crazy big flattened index of the CBVs.
            .exclude(path__startswith='ref/class-based-views/flattened-index')
        ).update(search=DOCUMENT_SEARCH_VECTOR)
        self.log('Successfully indexed %s item' % updated)
