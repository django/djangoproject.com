import codecs
import json
import os
from unittest import mock

import requests_mock
from django.core import management
from django.http import Http404
from django.test import RequestFactory, TestCase
from django_hosts.resolvers import reverse

from .models import (
    GithubItemCountMetric, Metric, RSSFeedMetric, TracTicketMetric,
)
from .views import index, metric_detail, metric_json


class ViewTests(TestCase):
    fixtures = ['dashboard_test_data']

    def setUp(self):
        self.factory = RequestFactory()

    def test_index(self):
        for MC in Metric.__subclasses__():
            for metric in MC.objects.filter(show_on_dashboard=True):
                metric.data.create(measurement=42)

        request = self.factory.get(reverse('dashboard-index', host='dashboard'))
        response = index(request)
        self.assertContains(response, 'Development dashboard')
        self.assertEqual(response.content.count(b'<div class="metric'), 13)
        self.assertEqual(response.content.count(b'42'), 13)

    def test_metric(self):
        TracTicketMetric.objects.get(slug='new-tickets-week').data.create(measurement=42)
        request = self.factory.get(reverse('metric-detail', args=['new-tickets-week'],
                                           host='dashboard'))
        response = metric_detail(request, 'new-tickets-week')
        self.assertContains(response, 'Development dashboard')

    def test_metric_404(self):
        request = self.factory.get(reverse('metric-detail', args=['new-tickets-week'],
                                           host='dashboard'))
        with self.assertRaisesRegex(Http404, r'Could not find metric with slug [\w-]+'):
            metric_detail(request, '404')

    def test_metric_json(self):
        TracTicketMetric.objects.get(slug='new-tickets-week').data.create(measurement=42)
        request = self.factory.get(reverse('metric-json', args=['new-tickets-week'],
                                           host='dashboard'))
        response = metric_json(request, 'new-tickets-week')
        self.assertEqual(json.loads(response.content.decode())['data'][0][1], 42)
        self.assertEqual(response.status_code, 200)


class MetricMixin:

    def test_str(self):
        self.assertEqual(str(self.instance), self.instance.name)

    def test_get_absolute_url(self):
        url_path = '/metric/%s/' % self.instance.slug
        self.assertTrue(url_path in self.instance.get_absolute_url())


class TracTicketMetricTestCase(TestCase, MetricMixin):
    fixtures = ['dashboard_test_data']

    def setUp(self):
        super().setUp()
        self.instance = TracTicketMetric.objects.last()

    @mock.patch('xmlrpc.client.ServerProxy')
    def test_fetch(self, mock_server_proxy):
        self.instance.fetch()
        self.assertTrue(mock_server_proxy.client.query.assert_called_with)


class RSSFeedMetricTestCase(TestCase, MetricMixin):
    fixtures = ['dashboard_test_data']
    feed_url = 'https://code.djangoproject.com/timeline?changeset=on&max=0&daysback=7&format=rss'
    fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'rss_feed_metric.xml')

    def setUp(self):
        super().setUp()
        self.instance = RSSFeedMetric.objects.last()

    @requests_mock.mock()
    def test_fetch(self, mocker):
        with codecs.open(self.fixtures_path, 'r', 'utf-8') as fixtures:
            feed_items = fixtures.read()
        mocker.get(self.feed_url, text=feed_items)
        self.assertEqual(self.instance.fetch(), 177)


class GithubItemCountMetricTestCase(TestCase, MetricMixin):
    fixtures = ['dashboard_test_data']
    api_url1 = 'https://api.github.com/repos/django/django/pulls?state=closed&per_page=100&page=1'
    api_url2 = 'https://api.github.com/repos/django/django/pulls?state=closed&per_page=100&page=2'

    def setUp(self):
        super().setUp()
        self.instance = GithubItemCountMetric.objects.last()

    @requests_mock.mock()
    def test_fetch(self, mocker):
        # faking a JSON output with 100 items first
        mocker.get(self.api_url1, text=json.dumps([{'id': i} for i in range(100)]))
        # and then with 42 items on the second page
        mocker.get(self.api_url2, text=json.dumps([{'id': i} for i in range(42)]))
        self.assertEqual(self.instance.fetch(), 142)


class UpdateMetricCommandTestCase(TestCase):
    github_url = 'https://api.github.com/repos/django/django/pulls?state=closed&per_page=100&page=1'

    def setUp(self):
        GithubItemCountMetric.objects.create(
            name='Pull Requests (Closed)',
            link_url="https://github.com/django/django/pulls",
            period="instant",
            unit_plural="pull requests",
            slug="pull-requests-closed",
            unit="pull request",
            api_url="https://api.github.com/repos/django/django/pulls?state=closed"
        )

    @requests_mock.mock()
    @mock.patch('dashboard.utils.reset_generation_key')
    def test_update_metric(self, mocker, mock_reset_generation_key):
        mocker.get(self.github_url, text=json.dumps([{'id': i} for i in range(10)]))
        management.call_command('update_metrics', verbosity=0)
        self.assertTrue(mock_reset_generation_key.called)
        data = GithubItemCountMetric.objects.last().data.last()
        self.assertEqual(data.measurement, 10)
