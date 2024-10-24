import time

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Document


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Update Document's search vector field in an atomic transaction.

        Inside an atomic transaction all not null search vector values are set
        to null and than the field are updated using the document definition.
        """
        _started_at = time.time()
        with transaction.atomic():
            Document.objects.search_reset()
            updated_documents = Document.objects.search_update()
        elapsed = time.time() - _started_at
        if options["verbosity"] >= 2:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Indexed {updated_documents} documents in {elapsed:.03}s."
                )
            )
