from django.core.management import BaseCommand, call_command

from ...models import Category, Metric


class Command(BaseCommand):
    help = 'Output pretty-printed JSON representations of the dashboard model '\
           'objects that should persist from installation to installation. '\
           'Primarily used for updating "dashboard_production_metrics.json".'

    def handle(self, **options):
        model_names = [m.__name__ for m in Metric.__subclasses__()]
        # Not strictly necessary, but ensures this code stays in sync with
        # models.py:
        model_names += [
            Category.__name__,
        ]
        call_command('dumpdata', *['dashboard.%s' % m for m in model_names],
                     indent=4)
