# -*- coding: utf-8 -*-
import json
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.test import TestCase, RequestFactory
from django_hosts.resolvers import reverse
import mock
import rmoq

from .models import TracTicketMetric, RSSFeedMetric, GithubItemCountMetric, Metric
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
        self.assertContains(response, 'Django development dashboard')
        self.assertEqual(response.content.count('<div class="metric'), 13)
        self.assertEqual(response.content.count('42'), 13)

    def test_metric(self):
        TracTicketMetric.objects.get(slug='new-tickets-week').data.create(measurement=42)
        request = self.factory.get(reverse('metric-detail', args=['new-tickets-week'],
                                           host='dashboard'))
        response = metric_detail(request, 'new-tickets-week')
        self.assertContains(response, 'Django development dashboard')

    def test_metric_404(self):
        request = self.factory.get(reverse('metric-detail', args=['new-tickets-week'],
                                           host='dashboard'))
        self.assertRaisesRegexp(
            Http404,
            'Could not find metric with slug [\w-]+',
            metric_detail,
            request,
            '404'
        )

    def test_metric_json(self):
        TracTicketMetric.objects.get(slug='new-tickets-week').data.create(measurement=42)
        request = self.factory.get(reverse('metric-json', args=['new-tickets-week'],
                                           host='dashboard'))
        response = metric_json(request, 'new-tickets-week')
        self.assertEqual(json.loads(response.content)['data'][0][1], 42)
        self.assertEqual(response.status_code, 200)


class MetricMixin(object):

    def test_get_absolute_url(self):
        self.assertEqual(
            self.instance.get_absolute_url(),
            'http://dashboard.djangoproject.dev:8000/metric/%s/' % self.instance.slug
        )


class TracTicketMetricTestCase(TestCase, MetricMixin):
    fixtures = ['dashboard_test_data']

    def setUp(self):
        super(TracTicketMetricTestCase, self).setUp()
        self.instance = TracTicketMetric.objects.last()

    @mock.patch('xmlrpclib.ServerProxy')
    def test_fetch(self, mock_server_proxy):
        self.instance.fetch()
        self.assertTrue(mock_server_proxy.client.query.assert_called_with)


class RSSFeedMetricTestCase(TestCase, MetricMixin):
    fixtures = ['dashboard_test_data']

    def setUp(self):
        super(RSSFeedMetricTestCase, self).setUp()
        self.instance = RSSFeedMetric.objects.last()

    @rmoq.activate('dashboard/fixtures')
    def test_fetch(self):
        self.assertEqual(self.instance.fetch(), 177)


class GithubItemCountMetricTestCase(TestCase, MetricMixin):
    fixtures = ['dashboard_test_data']

    def setUp(self):
        super(GithubItemCountMetricTestCase, self).setUp()
        self.instance = GithubItemCountMetric.objects.last()

    @rmoq.activate('dashboard/fixtures')
    def test_fetch(self):
        self.assertEqual(self.instance.fetch(), 101)
