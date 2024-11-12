from datetime import UTC, date, datetime
from operator import attrgetter

import time_machine
from django.test import SimpleTestCase, TestCase

from .models import (
    Attachment,
    Milestone,
    Revision,
    Ticket,
    TicketChange,
    TicketCustom,
    Version,
    Wiki,
)
from .testutils import TracDBCreateDatabaseMixin
from .tractime import (
    datetime_to_timestamp,
    dayrange,
    time_property,
    timestamp_to_datetime,
)


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
        if "time" in kwargs:
            assert "_time" not in kwargs
            kwargs["_time"] = datetime_to_timestamp(kwargs.pop("time"))

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

    @time_machine.travel("2024-10-24T14:30:00+00:00")
    def test_from_querystring_time_today_same_day(self):
        self._create_ticket(
            summary="test",
            time=datetime.fromisoformat("2024-10-24T10:30:00+00:00"),
        )
        self.assertTicketsEqual(
            Ticket.objects.from_querystring("time=today.."), ["test"]
        )

    @time_machine.travel("2024-10-24T14:30:00+00:00")
    def test_from_querystring_time_today_previous_day_less_than_24h(self):
        self._create_ticket(
            summary="test",
            # previous day, but still within 24h
            time=datetime.fromisoformat("2024-10-23T20:30:00+00:00"),
        )
        self.assertTicketsEqual(Ticket.objects.from_querystring("time=today.."), [])

    @time_machine.travel("2024-10-24T14:30:00+00:00")
    def test_from_querystring_time_today_previous_day_more_than_24h(self):
        self._create_ticket(
            summary="test",
            # previous day, more than 24h ago
            time=datetime.fromisoformat("2024-10-23T10:30:00+00:00"),
        )
        self.assertTicketsEqual(Ticket.objects.from_querystring("time=today.."), [])

    @time_machine.travel("2024-10-24T14:30:00+00:00")
    def test_from_querystring_time_thisweek(self):
        self._create_ticket(
            summary="test",
            time=datetime.fromisoformat("2024-10-21T10:30:00+00:00"),
        )
        self._create_ticket(
            summary="too old",
            time=datetime.fromisoformat("2024-10-15T10:30:00+00:00"),
        )
        self.assertTicketsEqual(
            Ticket.objects.from_querystring("time=thisweek.."), ["test"]
        )

    def test_from_querystring_invalid_time(self):
        with self.assertRaises(ValueError):
            Ticket.objects.from_querystring("time=2024-10-24..")


class TracTimeTestCase(SimpleTestCase):
    def test_datetime_to_timestamp(self):
        testdata = [
            (datetime(1970, 1, 1, microsecond=1, tzinfo=UTC), 1),
            (datetime(1970, 1, 1, 0, 0, 1, tzinfo=UTC), 1_000_000),
            (datetime(1970, 1, 2, tzinfo=UTC), 24 * 3600 * 1_000_000),
        ]
        for dt, expected in testdata:
            with self.subTest(dt=dt):
                self.assertEqual(datetime_to_timestamp(dt), expected)

    def test_timestamp_to_datetime(self):
        testdata = [
            (1, datetime(1970, 1, 1, microsecond=1, tzinfo=UTC)),
            (1_000_000, datetime(1970, 1, 1, second=1, tzinfo=UTC)),
            (24 * 3600 * 1_000_000, datetime(1970, 1, 2, tzinfo=UTC)),
        ]
        for ts, expected in testdata:
            with self.subTest(ts=ts):
                self.assertEqual(timestamp_to_datetime(ts), expected)

    def test_time_property(self):
        class T:
            timestamp = 1
            prop = time_property("timestamp")

        self.assertEqual(T().prop.date(), date(1970, 1, 1))

    def test_dayrange_error_negative_day(self):
        with self.assertRaises(ValueError):
            dayrange(date.today(), -1)

    def test_dayrange_error_zero_day(self):
        with self.assertRaises(ValueError):
            dayrange(date.today(), 0)

    def test_dayrange_error_datetime(self):
        with self.assertRaises(TypeError):
            dayrange(datetime.now(), 1)

    def test_dayrange_1_day(self):
        offset = 6 * 3600 * 1_000_000  # offset between utc and chicago
        self.assertEqual(
            dayrange(date(1970, 1, 1), days=1),
            (offset, offset + 24 * 3600 * 1_000_000 - 1),
        )


class TimePropertyTest(SimpleTestCase):
    def test_time_property_on_all_fields(self):
        for model_class, field_name, property_name in [
            (Ticket, "_time", "time"),
            (Ticket, "_changetime", "changetime"),
            (TicketChange, "_time", "time"),
            (Version, "_time", "time"),
            (Milestone, "_due", "due"),
            (Milestone, "_completed", "completed"),
            (Revision, "_time", "time"),
            (Wiki, "_time", "time"),
            (Attachment, "_time", "time"),
        ]:
            with self.subTest(model=model_class, field=field_name):
                obj = model_class(**{field_name: 1_000_000})
                self.assertEqual(
                    getattr(obj, property_name),
                    datetime(1970, 1, 1, 0, 0, 1, tzinfo=UTC),
                )
