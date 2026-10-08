from datetime import timedelta, timezone as dt_timezone

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Event
from djangoproject.tests import ReleaseMixin


class DateTimeMixin:
    def setUp(self):
        self.now = timezone.now()
        self.yesterday = self.now - timedelta(days=1)
        self.tomorrow = self.now + timedelta(days=1)


class EventListViewTestCase(ReleaseMixin, DateTimeMixin, TestCase):
    def _make_event(self, **kwargs):
        defaults = {
            "headline": "Test Event",
            "external_url": "https://example.com",
            "date": self.tomorrow,
            "location": "Online",
            "is_active": True,
            "pub_date": self.yesterday,
        }
        defaults.update(kwargs)
        return Event.objects.create(**defaults)

    def test_page_status_200(self):
        """
        The events page returns HTTP 200.
        """
        response = self.client.get(reverse("events:index"))
        self.assertEqual(response.status_code, 200)

    def test_upcoming_events_shown(self):
        """
        Published future events appear in upcoming_events context.
        """
        event = self._make_event(headline="Future Event", date=self.tomorrow)
        response = self.client.get(reverse("events:index"))
        self.assertIn(event, response.context["upcoming_events"])

    def test_past_events_shown(self):
        """
        Published past events appear in past_events context.
        """
        event = self._make_event(headline="Past Event", date=self.yesterday)
        response = self.client.get(reverse("events:index"))
        self.assertIn(event, response.context["past_events"])

    def test_no_unpublished_events_shown(self):
        """
        Inactive events do not appear on the page.
        """
        self._make_event(
            headline="Inactive Future", date=self.tomorrow, is_active=False
        )
        self._make_event(headline="Inactive Past", date=self.yesterday, is_active=False)
        response = self.client.get(reverse("events:index"))
        self.assertQuerySetEqual(response.context["upcoming_events"], [])
        self.assertQuerySetEqual(response.context["past_events"], [])

    def test_no_future_pub_date_events_shown(self):
        """
        Events whose pub_date is in the future are not yet published.
        """
        self._make_event(
            headline="Not Yet Published",
            date=self.tomorrow,
            is_active=True,
            pub_date=self.tomorrow,
        )
        response = self.client.get(reverse("events:index"))
        self.assertQuerySetEqual(response.context["upcoming_events"], [])

    def test_search_by_name(self):
        """
        ?q= filters events by headline (case-insensitive).
        """
        match = self._make_event(headline="DjangoCon Europe", date=self.tomorrow)
        self._make_event(headline="PyCon US", date=self.tomorrow)
        response = self.client.get(reverse("events:index") + "?q=djangocon")
        self.assertIn(match, response.context["upcoming_events"])
        self.assertEqual(len(response.context["upcoming_events"]), 1)

    def test_search_by_location(self):
        """
        ?q= filters events by location (case-insensitive).
        """
        match = self._make_event(
            headline="Django Day", date=self.tomorrow, location="Berlin, Germany"
        )
        self._make_event(headline="Sprint", date=self.tomorrow, location="Remote")
        response = self.client.get(reverse("events:index") + "?q=berlin")
        self.assertIn(match, response.context["upcoming_events"])
        self.assertEqual(len(response.context["upcoming_events"]), 1)

    def test_search_no_results(self):
        """
        A non-matching query returns empty upcoming and past lists.
        """
        self._make_event(headline="DjangoCon US", date=self.tomorrow)
        response = self.client.get(reverse("events:index") + "?q=rustconf")
        self.assertQuerySetEqual(response.context["upcoming_events"], [])
        self.assertQuerySetEqual(response.context["past_events"], [])

    def test_search_query_in_context(self):
        """
        The search term is passed back to the template via context.
        """
        response = self.client.get(reverse("events:index") + "?q=djangocon")
        self.assertEqual(response.context["query"], "djangocon")

    def test_empty_query_returns_all(self):
        """
        An empty ?q= returns all published events (no filtering).
        """
        future = self._make_event(headline="Future Event", date=self.tomorrow)
        past = self._make_event(headline="Past Event", date=self.yesterday)
        response = self.client.get(reverse("events:index") + "?q=")
        self.assertIn(future, response.context["upcoming_events"])
        self.assertIn(past, response.context["past_events"])

    def test_filter_by_location_param(self):
        """
        ?location= filters events specifically by location parameter.
        """
        match = self._make_event(
            headline="Berlin Conf", date=self.tomorrow, location="Berlin, Germany"
        )
        self._make_event(
            headline="Paris Conf", date=self.tomorrow, location="Paris, France"
        )
        response = self.client.get(reverse("events:index") + "?location=Berlin")
        self.assertIn(match, response.context["upcoming_events"])
        self.assertEqual(len(response.context["upcoming_events"]), 1)
        self.assertEqual(response.context["selected_location"], "Berlin")

    def test_filter_by_year_param(self):
        """
        ?year= filters events specifically by year parameter.
        """
        d_2025 = timezone.datetime(2025, 6, 15, tzinfo=dt_timezone.utc)
        d_2026 = timezone.datetime(2026, 6, 15, tzinfo=dt_timezone.utc)
        event_2025 = self._make_event(headline="2025 Event", date=d_2025)
        event_2026 = self._make_event(headline="2026 Event", date=d_2026)

        response = self.client.get(reverse("events:index") + f"?year={d_2025.year}")
        self.assertIn(event_2025, response.context["past_events"])
        self.assertNotIn(event_2026, response.context["upcoming_events"])
        self.assertEqual(response.context["selected_year"], str(d_2025.year))

    def test_filter_options_in_context(self):
        """
        Locations and years for published events are passed in context.
        """
        self._make_event(
            headline="Tokyo Event", location="Tokyo, Japan", date=self.tomorrow
        )
        self._make_event(
            headline="London Event", location="London, UK", date=self.yesterday
        )

        response = self.client.get(reverse("events:index"))
        self.assertIn("Tokyo, Japan", response.context["locations"])
        self.assertIn("London, UK", response.context["locations"])
        self.assertIn(self.tomorrow.year, response.context["years"])
