from datetime import timedelta

from django.test import TestCase
from django.test.utils import captured_stderr

from . import DateTimeMixin
from ..models import Entry, Event


class EntryTestCase(DateTimeMixin, TestCase):
    def test_manager_active(self):
        """
        Make sure that the Entry manager's `active` method works
        """
        Entry.objects.create(pub_date=self.now, is_active=False, headline='inactive')
        Entry.objects.create(pub_date=self.now, is_active=True, headline='active')

        self.assertQuerysetEqual(Entry.objects.published(), ['active'], transform=lambda entry: entry.headline)

    def test_manager_published(self):
        """
        Make sure that the Entry manager's `published` method works
        """
        Entry.objects.create(pub_date=self.yesterday, is_active=False, headline='past inactive')
        Entry.objects.create(pub_date=self.yesterday, is_active=True, headline='past active')
        Entry.objects.create(pub_date=self.tomorrow, is_active=False, headline='future inactive')
        Entry.objects.create(pub_date=self.tomorrow, is_active=True, headline='future active')

        self.assertQuerysetEqual(Entry.objects.published(), ['past active'], transform=lambda entry: entry.headline)

    def test_docutils_safe(self):
        """
        Make sure docutils' file inclusion directives are disabled by default.
        """
        with captured_stderr() as self.docutils_stderr:
            entry = Entry.objects.create(
                pub_date=self.now, is_active=True, headline='active', content_format='reST',
                body='.. raw:: html\n    :file: somefile\n'
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
