from django.core.management.base import BaseCommand

from sorl.thumbnail import default
from sorl.thumbnail.images import delete_all_thumbnails

VALID_LABELS = ['cleanup', 'clear', 'clear_delete_referenced', 'clear_delete_all']


class Command(BaseCommand):
    help = "Handles thumbnails and key-value store"
    missing_args_message = "Enter a valid operation: {}".format(
        ", ".join(VALID_LABELS)
    )

    def add_arguments(self, parser):
        parser.add_argument('args', choices=VALID_LABELS, nargs=1)

    def handle(self, *labels, **options):
        verbosity = int(options.get('verbosity'))
        label = labels[0]

        if label == 'cleanup':
            if verbosity >= 1:
                self.stdout.write("Cleanup thumbnails", ending=' ... ')

            default.kvstore.cleanup()

            if verbosity >= 1:
                self.stdout.write("[Done]")

            return

        if label == 'clear_delete_referenced':
            if verbosity >= 1:
                self.stdout.write(
                    "Delete all thumbnail files referenced in Key Value Store",
                    ending=' ... '
                )

            default.kvstore.delete_all_thumbnail_files()

            if verbosity >= 1:
                self.stdout.write('[Done]')

        if verbosity >= 1:
            self.stdout.write("Clear the Key Value Store", ending=' ... ')

        default.kvstore.clear()

        if verbosity >= 1:
            self.stdout.write('[Done]')

        if label == 'clear_delete_all':
            if verbosity >= 1:
                self.stdout.write("Delete all thumbnail files in THUMBNAIL_PREFIX", ending=' ... ')

            delete_all_thumbnails()

            if verbosity >= 1:
                self.stdout.write('[Done]')

    def create_parser(self, prog_name, subcommand, **kwargs):
        kwargs['epilog'] = (
            "Documentation: https://sorl-thumbnail.readthedocs.io/en/latest/management.html"
        )
        return super().create_parser(prog_name, subcommand, **kwargs)
