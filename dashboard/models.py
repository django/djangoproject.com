import ast
import calendar
import datetime
import xmlrpc.client

import feedparser
import requests
from django.conf import settings
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import connections, models
from django_hosts.resolvers import reverse

METRIC_PERIOD_INSTANT = 'instant'
METRIC_PERIOD_DAILY = 'daily'
METRIC_PERIOD_WEEKLY = 'weekly'
METRIC_PERIOD_CHOICES = (
    (METRIC_PERIOD_INSTANT, 'Instant'),
    (METRIC_PERIOD_DAILY, 'Daily'),
    (METRIC_PERIOD_WEEKLY, 'Weekly'),
)


class Category(models.Model):
    name = models.CharField(max_length=300)
    position = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Metric(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField()
    category = models.ForeignKey(Category, blank=True, null=True,
                                 on_delete=models.SET_NULL)
    position = models.PositiveSmallIntegerField(default=1)
    data = GenericRelation('Datum')
    show_on_dashboard = models.BooleanField(default=True)
    show_sparkline = models.BooleanField(default=True)
    period = models.CharField(max_length=15, choices=METRIC_PERIOD_CHOICES,
                              default=METRIC_PERIOD_INSTANT)
    unit = models.CharField(max_length=100)
    unit_plural = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("metric-detail", args=[self.slug], host='dashboard')

    @property
    def display_position(self):
        cat_position = -1 if self.category is None else self.category.position
        return cat_position, self.position

    def gather_data(self, since):
        """
        Gather all the data from this metric since a given date.

        Returns a list of (timestamp, value) tuples. The timestamp is a Unix
        timestamp, converted from localtime to UTC.
        """
        if self.period == METRIC_PERIOD_INSTANT:
            return self._gather_data_instant(since)
        elif self.period == METRIC_PERIOD_DAILY:
            return self._gather_data_periodic(since, 'day')
        elif self.period == METRIC_PERIOD_WEEKLY:
            return self._gather_data_periodic(since, 'week')
        else:
            raise ValueError("Unknown period: %s", self.period)

    def _gather_data_instant(self, since):
        """
        Gather data from an "instant" metric.

        Instant metrics change every time we measure them, so they're easy:
        just return every single measurement.
        """
        data = (self.data.filter(timestamp__gt=since)
                         .order_by('timestamp')
                         .values_list('timestamp', 'measurement'))
        return [(calendar.timegm(t.timetuple()), m) for (t, m) in data]

    def _gather_data_periodic(self, since, period):
        """
        Gather data from "periodic" merics.

        Period metrics are reset every day/week/month and count up as the period
        goes on. Think "commits today" or "new tickets this week".

        XXX I'm not completely sure how to deal with this since time zones wreak
        havoc, so there's right now a hard-coded offset which doesn't really
        scale but works for now.
        """
        OFFSET = "2 hours"  # HACK!
        ctid = ContentType.objects.get_for_model(self).id

        c = connections['default'].cursor()
        c.execute('''SELECT
                        DATE_TRUNC(%s, timestamp - INTERVAL %s),
                        MAX(measurement)
                     FROM dashboard_datum
                     WHERE content_type_id = %s
                       AND object_id = %s
                       AND timestamp >= %s
                     GROUP BY 1;''', [period, OFFSET, ctid, self.id, since])
        return [(calendar.timegm(t.timetuple()), float(m)) for (t, m) in c.fetchall()]


class TracTicketMetric(Metric):
    query = models.TextField()

    def fetch(self):
        s = xmlrpc.client.ServerProxy(settings.TRAC_RPC_URL)
        return len(s.ticket.query(self.query + "&max=0"))

    def link(self):
        return "%squery?%s&desc=1&order=changetime" % (settings.TRAC_URL, self.query)


class RSSFeedMetric(Metric):
    feed_url = models.URLField(max_length=1000)
    link_url = models.URLField(max_length=1000)

    def fetch(self):
        return len(feedparser.parse(requests.get(self.feed_url).text).entries)

    def link(self):
        return self.link_url


class GithubItemCountMetric(Metric):
    """Example: https://api.github.com/repos/django/django/pulls?state=open"""
    api_url = models.URLField(max_length=1000)
    link_url = models.URLField(max_length=1000)

    def fetch(self):
        """
        Request the specified GitHub API URL with 100 items per page. Loop over
        the pages until no page left. Return total item count.
        """
        count = 0
        page = 1
        number_of_items_on_page = 101
        while number_of_items_on_page >= 100:
            r = requests.get(self.api_url, params={
                'page': page,
                'per_page': 100
            })
            number_of_items_on_page = len(r.json())
            count += number_of_items_on_page
            page += 1
        return count

    def link(self):
        return self.link_url


class JenkinsFailuresMetric(Metric):
    """
    Track failures of a job/build. Uses the Python flavor of the Jenkins REST
    API.
    """
    jenkins_root_url = models.URLField(
        verbose_name='Jenkins instance root URL',
        max_length=1000,
        help_text='E.g. http://ci.djangoproject.com/',
    )
    build_name = models.CharField(
        max_length=100,
        help_text='E.g. Django Python3',
    )
    is_success_cnt = models.BooleanField(
        default=False,
        verbose_name='Should the metric be a value representing success ratio?',
        help_text='E.g. if there are 50 tests of which 30 are failing the value of this metric '
                  'will be 20 (or 40%.)',
    )
    is_percentage = models.BooleanField(
        default=False,
        verbose_name='Should the metric be a percentage value?',
        help_text='E.g. if there are 50 tests of which 30 are failing the value of this metric '
                  'will be 60%.',
    )

    def urljoin(self, *parts):
        return '/'.join(p.strip('/') for p in parts)

    def _fetch(self):
        """
        Actually get the values we are interested in by using the Jenkins REST
        API (https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API)
        """
        api_url = self.urljoin(self.link(), 'api/python')
        job_desc = requests.get(api_url)
        job_dict = ast.literal_eval(job_desc.text)
        build_ptr_dict = job_dict['lastCompletedBuild']
        build_url = self.urljoin(build_ptr_dict['url'], 'api/python')
        build_desc = requests.get(build_url)
        build_dict = ast.literal_eval(build_desc.text)
        return (build_dict['actions'][4]['failCount'], build_dict['actions'][4]['totalCount'])

    def _calculate(self, failures, total):
        """Calculate the metric value."""
        if self.is_success_cnt:
            value = total - failures
        else:
            value = failures
        if self.is_percentage:
            if not total:
                return 0
            value = (value * 100) / total
        return value

    def fetch(self):
        failures, total = self._fetch()
        return self._calculate(failures, total)

    def link(self):
        return self.urljoin(self.jenkins_root_url, 'job', self.build_name)


class Datum(models.Model):
    metric = GenericForeignKey()
    content_type = models.ForeignKey(ContentType, related_name='+', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    measurement = models.BigIntegerField()

    class Meta:
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'
        verbose_name_plural = 'data'

    def __str__(self):
        return "%s at %s: %s" % (self.metric, self.timestamp, self.measurement)
