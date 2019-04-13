# encoding=utf-8

from __future__ import unicode_literals, print_function

import sys

from django.core.management.base import LabelCommand, CommandError

from sorl.thumbnail import default
from sorl.thumbnail.images import delete_all_thumbnails


class Command(LabelCommand):
    help = (
        'Handles thumbnails and key value store'
    )
    missing_args_message = 'Enter one of [cleanup, clear clear_delete_referenced clear_delete_all]'

    def handle(self, *labels, **options):
        verbosity = int(options.get('verbosity'))

        # Django 1.4 compatibility fix
        stdout = options.get('stdout', None)
        stdout = stdout if stdout else sys.stdout

        stderr = options.get('stderr', None)
        stderr = stderr if stderr else sys.stderr

        if not labels:
            print(self.print_help('thumbnail', ''), file=stderr)
            sys.exit(1)

        if len(labels) != 1:
            raise CommandError('`%s` is not a valid argument' % labels)

        label = labels[0]

        if label not in ['cleanup', 'clear', 'clear_delete_referenced', 'clear_delete_all']:
            raise CommandError('`%s` unknown action' % label)

        if label == 'cleanup':
            if verbosity >= 1:
                print("Cleanup thumbnails", end=' ... ', file=stdout)

            default.kvstore.cleanup()

            if verbosity >= 1:
                print("[Done]", file=stdout)

            return

        if label == 'clear_delete_referenced':
            if verbosity >= 1:
                print("Delete all thumbnail files referenced in " +
                      "Key Value Store", end=' ... ', file=stdout)

            default.kvstore.delete_all_thumbnail_files()

            if verbosity >= 1:
                print('[Done]', file=stdout)

        if verbosity >= 1:
            print("Clear the Key Value Store", end=' ... ', file=stdout)

        default.kvstore.clear()

        if verbosity >= 1:
            print('[Done]', file=stdout)

        if label == 'clear_delete_all':
            if verbosity >= 1:
                print("Delete all thumbnail files in THUMBNAIL_PREFIX", end=' ... ', file=stdout)

            delete_all_thumbnails()

            if verbosity >= 1:
                print('[Done]', file=stdout)
