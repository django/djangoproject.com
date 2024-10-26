from datetime import date, timedelta

import time_machine
from django.core.management.base import CommandError, LabelCommand
from django.db.models import Case, Max, Min, When

from ...models import TracTicketMetric


def _get_data(metric, options):
    """
    Return a queryset of Datum instances for the given metric, taking into
    account the from_date/to_date keys of the given options dict.
    """
    queryset = metric.data.all()
    if options["from_date"]:
        queryset = queryset.filter(timestamp__date__gte=options["from_date"])
    if options["to_date"]:
        queryset = queryset.filter(timestamp__date__lte=options["to_date"])
    return queryset


def _daterange(queryset):
    """
    Given a queryset of Datum objects, generate all dates (as date objects)
    between the earliest and latest data points in the queryset.
    """
    aggregated = queryset.aggregate(
        start=Min("timestamp__date"), end=Max("timestamp__date")
    )
    if aggregated["start"] is None or aggregated["end"] is None:
        raise ValueError("queryset cannot be empty")

    d = aggregated["start"]
    while d <= aggregated["end"]:
        yield d
        d += timedelta(days=1)


def _refetched_case_when(dates, metric):
    """
    Refetch the given metric for all the given dates and build a CASE database
    expression with one WHEN per date.
    """
    whens = []
    for d in dates:
        with time_machine.travel(d):
            whens.append(When(timestamp__date=d, then=metric.fetch()))
    return Case(*whens)


class Command(LabelCommand):
    help = "Retroactively refetch measurements for Trac metrics."
    label = "slug"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--yes", action="store_true", help="Commit the changes to the database"
        )
        parser.add_argument(
            "--from-date",
            type=date.fromisoformat,
            help="Restrict the timestamp range (ISO format)",
        )
        parser.add_argument(
            "--to-date",
            type=date.fromisoformat,
            help="Restrict the timestamp range (ISO format)",
        )

    def handle_label(self, label, **options):
        try:
            metric = TracTicketMetric.objects.get(slug=label)
        except TracTicketMetric.DoesNotExist as e:
            raise CommandError from e

        verbose = int(options["verbosity"]) > 0

        if verbose:
            self.stdout.write(f"Fixing metric {label}...")
        dataset = _get_data(metric, options)

        if options["yes"]:
            dates = _daterange(dataset)
            updated_measurement_expression = _refetched_case_when(dates, metric)
            updated = dataset.update(measurement=updated_measurement_expression)
            if verbose:
                self.stdout.write(self.style.SUCCESS(f"{updated} rows updated"))
        else:
            if verbose:
                self.stdout.write(f"{dataset.count()} rows will be updated.")
                self.stdout.write("Re-run the command with --yes to apply the change")
