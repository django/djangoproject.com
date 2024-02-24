from operator import attrgetter

from django.test import TestCase

from .models import Revision, Ticket, TicketCustom
from .testutils import TracDBCreateDatabaseMixin


class TestModels(TestCase):
    def test_router(self):
        self.assertEqual(Revision.objects.db, "trac")


class TicketTestCase(TracDBCreateDatabaseMixin, TestCase):
    databases = {"trac"}

    def _create_ticket(self, custom=None, **kwargs):
        """
        A factory to create a Ticket, with optional TicketCustom instances attached.
        """
        if custom is None:
            custom = {}

        ticket = Ticket.objects.create(**kwargs)
        TicketCustom.objects.bulk_create(
            [
                TicketCustom(ticket=ticket, name=name, value=value)
                for name, value in custom.items()
            ]
        )
        return ticket

    def assertTicketsEqual(
        self, queryset, expected, transform=attrgetter("summary"), ordered=False
    ):
        """
        A wrapper around assertQuerysetEqual with some useful defaults
        """
        self.assertQuerySetEqual(
            queryset, expected, transform=transform, ordered=ordered
        )

    def test_ticket_table_exist_in_testdb(self):
        self._create_ticket(summary="test", custom={"x": "y"})
        self.assertTicketsEqual(Ticket.objects.all(), ["test"])
        self.assertQuerySetEqual(
            TicketCustom.objects.all(),
            [("x", "y")],
            transform=attrgetter("name", "value"),
            ordered=False,
        )

    def test_with_custom(self):
        self._create_ticket(summary="test1", custom={"x": "A", "y": "B"})
        self._create_ticket(summary="test2", custom={"z": "C"})

        self.assertQuerySetEqual(
            Ticket.objects.with_custom().order_by("summary"),
            [
                ("test1", {"x": "A", "y": "B"}),
                ("test2", {"z": "C"}),
            ],
            transform=attrgetter("summary", "custom"),
        )

    def test_with_custom_lookup(self):
        self._create_ticket(summary="test", custom={"x": "A", "y": "B"})

        self.assertTicketsEqual(
            Ticket.objects.with_custom().filter(custom__x="A"),
            [("test")],
        )

    def test_with_custom_lookup_multiple(self):
        self._create_ticket(summary="test1", custom={"x": "A", "y": "A"})
        self._create_ticket(summary="test2", custom={"x": "A", "y": "B"})
        self._create_ticket(summary="test3", custom={"x": "B", "y": "A"})

        self.assertTicketsEqual(
            Ticket.objects.with_custom().filter(custom__x="A", custom__y="A"),
            [("test1")],
        )

    def test_from_querystring_model_field(self):
        self._create_ticket(summary="test1", severity="high")
        self._create_ticket(summary="test2", severity="low")

        self.assertTicketsEqual(
            Ticket.objects.from_querystring("severity=high"),
            ["test1"],
        )

    def test_from_querystring_model_field_multiple(self):
        self._create_ticket(summary="test1", severity="high", resolution="new")
        self._create_ticket(summary="test2", severity="high", resolution="fixed")
        self._create_ticket(summary="test3", severity="low", resolution="new")
        self._create_ticket(summary="test4", severity="low", resolution="fixed")

        self.assertTicketsEqual(
            Ticket.objects.from_querystring("severity=high&resolution=new"),
            ["test1"],
        )

    def test_from_querystring_model_field_negative(self):
        self._create_ticket(summary="test1", severity="high")
        self._create_ticket(summary="test2", severity="low")

        self.assertTicketsEqual(
            Ticket.objects.from_querystring("severity=!high"),
            ["test2"],
        )

    def test_from_querystring_model_field_negative_multiple(self):
        self._create_ticket(summary="test1", severity="high", resolution="new")
        self._create_ticket(summary="test2", severity="high", resolution="fixed")
        self._create_ticket(summary="test3", severity="low", resolution="new")
        self._create_ticket(summary="test4", severity="low", resolution="fixed")

        self.assertTicketsEqual(
            Ticket.objects.from_querystring("severity=!low&resolution=!fixed"),
            ["test1"],
        )

    def test_from_querystring_custom_field(self):
        self._create_ticket(summary="test1", custom={"stage": "unreviewed"})
        self._create_ticket(summary="test2", custom={"stage": "reviewed"})

        self.assertTicketsEqual(
            Ticket.objects.from_querystring("stage=reviewed"),
            ["test2"],
        )

    def test_from_querystring_custom_field_negative(self):
        self._create_ticket(summary="test1", custom={"stage": "unreviewed"})
        self._create_ticket(summary="test2", custom={"stage": "reviewed"})

        self.assertTicketsEqual(
            Ticket.objects.from_querystring("stage=!reviewed"),
            ["test1"],
        )

    def test_from_querystring_model_and_custom_field_together(self):
        self._create_ticket(
            summary="test1", severity="high", custom={"stage": "unreviewed"}
        )
        self._create_ticket(
            summary="test2", severity="high", custom={"stage": "reviewed"}
        )
        self._create_ticket(
            summary="test3", severity="low", custom={"stage": "unreviewed"}
        )
        self._create_ticket(
            summary="test4", severity="low", custom={"stage": "reviewed"}
        )

        self.assertTicketsEqual(
            Ticket.objects.from_querystring("severity=high&stage=unreviewed"),
            ["test1"],
        )
