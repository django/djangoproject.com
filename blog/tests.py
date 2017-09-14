from datetime import timedelta
from test.support import captured_stderr

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Entry, Event
from .sitemaps import WeblogSitemap


class DateTimeMixin:
    def setUp(self):
        self.now = timezone.now()
        self.yesterday = self.now - timedelta(days=1)
        self.tomorrow = self.now + timedelta(days=1)


class EntryTestCase(DateTimeMixin, TestCase):
    def test_manager_active(self):
        """
        Make sure that the Entry manager's `active` method works
        """
        Entry.objects.create(pub_date=self.now, is_active=False, headline='inactive', slug='a')
        Entry.objects.create(pub_date=self.now, is_active=True, headline='active', slug='b')

        self.assertQuerysetEqual(Entry.objects.published(), ['active'], transform=lambda entry: entry.headline)

    def test_manager_published(self):
        """
        Make sure that the Entry manager's `published` method works
        """
        Entry.objects.create(pub_date=self.yesterday, is_active=False, headline='past inactive', slug='a')
        Entry.objects.create(pub_date=self.yesterday, is_active=True, headline='past active', slug='b')
        Entry.objects.create(pub_date=self.tomorrow, is_active=False, headline='future inactive', slug='c')
        Entry.objects.create(pub_date=self.tomorrow, is_active=True, headline='future active', slug='d')

        self.assertQuerysetEqual(Entry.objects.published(), ['past active'], transform=lambda entry: entry.headline)

    def test_docutils_safe(self):
        """
        Make sure docutils' file inclusion directives are disabled by default.
        """
        with captured_stderr() as self.docutils_stderr:
            entry = Entry.objects.create(
                pub_date=self.now, is_active=True, headline='active', content_format='reST',
                body='.. raw:: html\n    :file: somefile\n', slug='a',
            )
        self.assertIn('<p>&quot;raw&quot; directive disabled.</p>', entry.body_html)
        self.assertIn('.. raw:: html\n    :file: somefile', entry.body_html)


class EventTestCase(DateTimeMixin, TestCase):
    def test_manager_past_future(self):
        """
        Make sure that the Event manager's `past` and `future` methods works
        """
        Event.objects.create(date=self.yesterday, pub_date=self.now, headline='past')
        Event.objects.create(date=self.tomorrow, pub_date=self.now, headline='future')

        self.assertQuerysetEqual(Event.objects.future(), ['future'], transform=lambda event: event.headline)
        self.assertQuerysetEqual(Event.objects.past(), ['past'], transform=lambda event: event.headline)

    def test_manager_past_future_include_today(self):
        """
        Make sure that both .future() and .past() include today's events.
        """
        Event.objects.create(date=self.now, pub_date=self.now, headline='today')

        self.assertQuerysetEqual(Event.objects.future(), ['today'], transform=lambda event: event.headline)
        self.assertQuerysetEqual(Event.objects.past(), ['today'], transform=lambda event: event.headline)

    def test_past_future_ordering(self):
        """
        Make sure the that .future() and .past() use the actual date for ordering
        (and not the pub_date).
        """
        D = timedelta(days=1)
        Event.objects.create(date=self.yesterday - D, pub_date=self.yesterday - D, headline='a')
        Event.objects.create(date=self.yesterday, pub_date=self.yesterday, headline='b')

        Event.objects.create(date=self.tomorrow, pub_date=self.tomorrow, headline='c')
        Event.objects.create(date=self.tomorrow + D, pub_date=self.tomorrow + D, headline='d')

        self.assertQuerysetEqual(Event.objects.future(), ['c', 'd'], transform=lambda event: event.headline)
        self.assertQuerysetEqual(Event.objects.past(), ['b', 'a'], transform=lambda event: event.headline)


class ViewsTestCase(DateTimeMixin, TestCase):
    def test_no_past_upcoming_events(self):
        """
        Make sure there are no past event in the "upcoming events" sidebar (#399)
        """
        # We need a published entry on the index page so that it doesn't return a 404
        Entry.objects.create(pub_date=self.yesterday, is_active=True, slug='a')
        Event.objects.create(date=self.yesterday, pub_date=self.now, is_active=True, headline='Jezdezcon')
        response = self.client.get(reverse('weblog:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['events'], [])


class SitemapTests(DateTimeMixin, TestCase):

    def test_sitemap(self):
        entry = Entry.objects.create(pub_date=self.yesterday, is_active=True, headline='foo', slug='foo')
        sitemap = WeblogSitemap()
        urls = sitemap.get_urls()
        self.assertEqual(len(urls), 1)
        url_info = urls[0]
        self.assertEqual(url_info['location'], entry.get_absolute_url())
