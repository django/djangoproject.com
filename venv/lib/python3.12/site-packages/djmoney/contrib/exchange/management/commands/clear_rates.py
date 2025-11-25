from django.utils.module_loading import import_string

from djmoney.contrib.exchange.models import Rate

from ..base import BaseExchangeCommand


class Command(BaseExchangeCommand):
    help = "Clears exchange rates."

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--all",
            action="store_true",
            dest="all",
            help="Clear rates for all backends.",
            required=False,
            default=False,
        )

    def handle(self, *args, **options):
        if options["all"]:
            Rate.objects.all().delete()
            message = "Successfully cleared all rates"
        else:
            backend = import_string(options["backend"])
            Rate.objects.filter(backend=backend.name).delete()
            message = "Successfully cleared rates for %s" % backend.name
        self.success(message)
