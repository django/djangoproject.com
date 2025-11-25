from django.core.management.base import BaseCommand

from djmoney import settings


class BaseExchangeCommand(BaseCommand):
    """
    Basic command for exchange rates manipulation.
    Provides ``backend`` argument.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-b",
            "--backend",
            action="store",
            dest="backend",
            help="Importable string for custom exchange rates backend.",
            required=False,
            default=settings.EXCHANGE_BACKEND,
        )

    def success(self, message):
        self.stdout.write(self.style.SUCCESS(message))
