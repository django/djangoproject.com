import datetime
from optparse import make_option as Option

from django.core.management.base import BaseCommand

from ...search import DocumentDocType


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        Option("--using", default=None,
               help='The name of the connection to use'),
    )

    def log(self, msg, level=2):
        """
        Small log helper
        """
        if self.verbosity >= level:
            self.stdout.write(msg)

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        new_index_name = 'docs-%s' % datetime.datetime.now().isoformat().lower()
        index_results = DocumentDocType.index_all(
            index_name=new_index_name,
            using=options['using'],
        )
        for ok, item in index_results:
            id_ = item.get('index', {}).get('_id', item)
            if ok:
                self.log('Successfully indexed item %s' % id_)
            else:
                self.log('Failed indexing item %s' % id_)
        # Alias the main 'docs' index to the new one.
        DocumentDocType.alias_to_main_index(new_index_name, using=options['using'])
