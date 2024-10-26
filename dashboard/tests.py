import datetime
import json
from operator import attrgetter
from unittest import mock

import requests_mock
from django.core import management
from django.http import Http404
from django.test import RequestFactory, TestCase
from django_hosts.resolvers import reverse

from tracdb.models import Ticket
from tracdb.testutils import TracDBCreateDatabaseMixin
from tracdb.tractime import datetime_to_timestamp

from .models import (
    METRIC_PERIOD_DAILY,
    METRIC_PERIOD_WEEKLY,
    GithubItemCountMetric,
    GitHubSearchCountMetric,
    Metric,
    TracTicketMetric,
)
from .views import index, metric_detail, metric_json


class ViewTests(TestCase):
    fixtures = ["dashboard_test_data"]

    def setUp(self):
        self.factory = RequestFactory()

    def test_index(self):
        for MC in Metric.__subclasses__():
            for metric in MC.objects.filter(show_on_dashboard=True):
                metric.data.create(measurement=42)

        request = self.factory.get(reverse("dashboard-index", host="dashboard"))
        response = index(request)
        self.assertContains(response, "Development dashboard")
        self.assertEqual(response.content.count(b'<div class="metric'), 13)
        self.assertEqual(response.content.count(b"42"), 13)

    def test_metric(self):
        TracTicketMetric.objects.get(slug="new-tickets-week").data.create(
            measurement=42
        )
        request = self.factory.get(
            reverse("metric-detail", args=["new-tickets-week"], host="dashboard")
        )
        response = metric_detail(request, "new-tickets-week")
        self.assertContains(response, "Development dashboard")

    def test_metric_404(self):
        request = self.factory.get(
            reverse("metric-detail", args=["new-tickets-week"], host="dashboard")
        )
        with self.assertRaisesRegex(Http404, r"Could not find metric with slug [\w-]+"):
            metric_detail(request, "404")

    def test_metric_json(self):
        TracTicketMetric.objects.get(slug="new-tickets-week").data.create(
            measurement=42
        )
        request = self.factory.get(
            reverse("metric-json", args=["new-tickets-week"], host="dashboard")
        )
        response = metric_json(request, "new-tickets-week")
        self.assertEqual(json.loads(response.content.decode())["data"][0][1], 42)
        self.assertEqual(response.status_code, 200)


class MetricMixin:
    def test_str(self):
        self.assertEqual(str(self.instance), self.instance.name)

    def test_get_absolute_url(self):
        url_path = "/metric/%s/" % self.instance.slug
        self.assertTrue(url_path in self.instance.get_absolute_url())


class TracTicketMetricTestCase(TracDBCreateDatabaseMixin, TestCase):
    databases = {"default", "trac"}

    def test_fetch(self):
        Ticket.objects.create(status="new", priority="high")
        Ticket.objects.create(status="new", priority="low")
        Ticket.objects.create(status="closed", priority="high")
        Ticket.objects.create(status="closed", priority="low")
        metric = TracTicketMetric.objects.create(
            slug="test-tracticketmetric",
            name="test tracticketmetric",
            query="status=!closed&priority=high",
        )

        self.assertEqual(metric.fetch(), 1)


class GithubItemCountMetricTestCase(TestCase, MetricMixin):
    fixtures = ["dashboard_test_data"]
    api_url1 = (
        "https://api.github.com/repos/django/django/pulls"
        "?state=closed&per_page=100&page=1"
    )
    api_url2 = (
        "https://api.github.com/repos/django/django/pulls"
        "?state=closed&per_page=100&page=2"
    )

    def setUp(self):
        super().setUp()
        self.instance = GithubItemCountMetric.objects.last()

    @requests_mock.mock()
    def test_fetch(self, mocker):
        # faking a JSON output with 100 items first
        mocker.get(self.api_url1, text=json.dumps([{"id": i} for i in range(100)]))
        # and then with 42 items on the second page
        mocker.get(self.api_url2, text=json.dumps([{"id": i} for i in range(42)]))
        self.assertEqual(self.instance.fetch(), 142)


class GitHubSearchCountMetricTestCase(TestCase, MetricMixin):
    fixtures = ["dashboard_test_data"]
    api_url = (
        "https://api.github.com/search/commits?"
        "per_page=1&q=repo:django/django+committer-date:%s"
    )

    def setUp(self):
        super().setUp()
        self.instance = GitHubSearchCountMetric.objects.last()

    @requests_mock.mock()
    def test_fetch(self, mocker):
        today = datetime.date.today()
        week_start = today - datetime.timedelta(weeks=1)
        # Faking a daily JSON output with 4 items.
        mocker.get(
            self.api_url % today.isoformat(),
            text=json.dumps({"total_count": 4, "items": []}),
        )
        metric = GitHubSearchCountMetric.objects.filter(
            period=METRIC_PERIOD_DAILY
        ).last()
        self.assertEqual(metric.fetch(), 4)
        # Faking a weekly JSON output with 23 items.
        mocker.get(
            self.api_url % ">" + week_start.isoformat(),
            text=json.dumps({"total_count": 23, "items": []}),
        )
        metric = GitHubSearchCountMetric.objects.filter(
            period=METRIC_PERIOD_WEEKLY
        ).last()
        self.assertEqual(metric.fetch(), 23)


class UpdateMetricCommandTestCase(TestCase):
    github_url = (
        "https://api.github.com/repos/django/django/pulls"
        "?state=closed&per_page=100&page=1"
    )

    def setUp(self):
        GithubItemCountMetric.objects.create(
            name="Pull Requests (Closed)",
            link_url="https://github.com/django/django/pulls",
            period="instant",
            unit_plural="pull requests",
            slug="pull-requests-closed",
            unit="pull request",
            api_url="https://api.github.com/repos/django/django/pulls?state=closed",
        )

    @requests_mock.mock()
    @mock.patch("dashboard.utils.reset_generation_key")
    def test_update_metric(self, mocker, mock_reset_generation_key):
        mocker.get(self.github_url, text=json.dumps([{"id": i} for i in range(10)]))
        management.call_command("update_metrics", verbosity=0)
        self.assertTrue(mock_reset_generation_key.called)
        data = GithubItemCountMetric.objects.last().data.last()
        self.assertEqual(data.measurement, 10)


class FixTracMetricsCommandTestCase(TracDBCreateDatabaseMixin, TestCase):
    databases = {"default", "trac"}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        def dt(*args, **kwargs):
            kwargs.setdefault("tzinfo", datetime.UTC)
            return datetime.datetime(*args, **kwargs)

        def ts(*args, **kwargs):
            return datetime_to_timestamp(dt(*args, **kwargs))

        for day in range(7):
            Ticket.objects.create(_time=ts(2024, 1, day + 1))

        cls.metric_today = TracTicketMetric.objects.create(
            slug="today", query="time=today.."
        )
        cls.metric_week = TracTicketMetric.objects.create(
            slug="week", query="time=thisweek.."
        )

    def test_command_today(self):
        datum = self.metric_today.data.create(
            measurement=0, timestamp="2024-01-01T00:00:00"
        )
        management.call_command("fix_trac_metrics", "today", yes=True, verbosity=0)
        datum.refresh_from_db()
        self.assertEqual(datum.measurement, 1)

    def test_command_week(self):
        datum = self.metric_week.data.create(
            measurement=0, timestamp="2024-01-07T00:00:00"
        )
        management.call_command("fix_trac_metrics", "week", yes=True, verbosity=0)
        datum.refresh_from_db()
        self.assertEqual(datum.measurement, 7)

    def test_command_safe_by_default(self):
        datum = self.metric_today.data.create(
            measurement=0, timestamp="2024-01-01T00:00:00"
        )
        management.call_command("fix_trac_metrics", "today", verbosity=0)
        datum.refresh_from_db()
        self.assertEqual(datum.measurement, 0)

    def test_multiple_measurements(self):
        self.metric_today.data.create(measurement=0, timestamp="2024-01-01T00:00:00")
        self.metric_today.data.create(measurement=0, timestamp="2024-01-02T00:00:00")
        self.metric_today.data.create(measurement=0, timestamp="2024-01-03T00:00:00")
        management.call_command("fix_trac_metrics", "today", yes=True, verbosity=0)
        self.assertQuerySetEqual(
            self.metric_today.data.order_by("timestamp"),
            [1, 1, 1],
            transform=attrgetter("measurement"),
        )

    def test_option_from_date(self):
        self.metric_today.data.create(measurement=0, timestamp="2024-01-01T00:00:00")
        self.metric_today.data.create(measurement=0, timestamp="2024-01-02T00:00:00")
        self.metric_today.data.create(measurement=0, timestamp="2024-01-03T00:00:00")
        management.call_command(
            "fix_trac_metrics",
            "today",
            yes=True,
            from_date=datetime.date(2024, 1, 2),
            verbosity=0,
        )
        self.assertQuerySetEqual(
            self.metric_today.data.order_by("timestamp"),
            [0, 1, 1],
            transform=attrgetter("measurement"),
        )

    def test_option_to_date(self):
        self.metric_today.data.create(measurement=0, timestamp="2024-01-01T00:00:00")
        self.metric_today.data.create(measurement=0, timestamp="2024-01-02T00:00:00")
        self.metric_today.data.create(measurement=0, timestamp="2024-01-03T00:00:00")
        management.call_command(
            "fix_trac_metrics",
            "today",
            yes=True,
            to_date=datetime.date(2024, 1, 2),
            verbosity=0,
        )
        self.assertQuerySetEqual(
            self.metric_today.data.order_by("timestamp"),
            [1, 1, 0],
            transform=attrgetter("measurement"),
        )

    def test_option_both_to_and_from_date(self):
        self.metric_today.data.create(measurement=0, timestamp="2024-01-01T00:00:00")
        self.metric_today.data.create(measurement=0, timestamp="2024-01-02T00:00:00")
        self.metric_today.data.create(measurement=0, timestamp="2024-01-03T00:00:00")
        management.call_command(
            "fix_trac_metrics",
            "today",
            yes=True,
            from_date=datetime.date(2024, 1, 2),
            to_date=datetime.date(2024, 1, 2),
            verbosity=0,
        )
        self.assertQuerySetEqual(
            self.metric_today.data.order_by("timestamp"),
            [0, 1, 0],
            transform=attrgetter("measurement"),
        )
