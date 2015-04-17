from optparse import make_option as Option

from django.core.management.base import BaseCommand

from ...search import DocumentDocType


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        Option("--using", default=None,
               help='The name of the connection to use'),
        Option("-d", "--delete",
               default=False,
               dest='delete',
               action='store_true',
               help='Whether to delete the index or not'),
    )

    def log(self, msg, level='2'):
        """
        Small log helper
        """
        if self.verbosity >= level:
            self.stdout.write(msg)

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        for ok, item in DocumentDocType.index_all(using=options['using'],
                                                  delete=options['delete']):
            id_ = item.get('index', {}).get('_id', item)
            if ok:
                self.log('Successfully indexed item %s' % id_)
            else:
                self.log('Failed indexing item %s' % id_)
