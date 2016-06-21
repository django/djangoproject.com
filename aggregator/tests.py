import datetime

import requests_mock
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from docs.models import DocumentRelease
from releases.models import Release

from . import models
from .forms import FeedModelForm


class AggregatorTests(TestCase):

    @requests_mock.mock()
    def setUp(self, mocker):
        mocker.register_uri('POST', settings.PUSH_HUB, status_code=202)
        # document release necessary to fetch main page
        release, _ = Release.objects.get_or_create(
            version="1.4",
        )
        DocumentRelease.objects.update_or_create(
            release=release,
            lang='en',
            defaults={'is_default': True},
        )

        # Set up users who will get emailed
        g, _ = Group.objects.get_or_create(
            name=settings.FEED_APPROVERS_GROUP_NAME,
        )
        self.user, _ = User.objects.get_or_create(
            username="Mr. Potato",
            email="mr@potato.com",
        )
        self.user.groups.add(g)

        self.feed_type, _ = models.FeedType.objects.get_or_create(
            name="Test Feed Type",
            slug="test-feed-type",
            can_self_add=True,
        )

        self.approved_feed, _ = models.Feed.objects.get_or_create(
            title="Approved",
            feed_url="foo.com/rss/",
            public_url="foo.com/",
            approval_status=models.APPROVED_FEED,
            feed_type=self.feed_type,
        )
        self.denied_feed, _ = models.Feed.objects.get_or_create(
            title="Denied",
            feed_url="bar.com/rss/",
            public_url="bar.com/",
            approval_status=models.DENIED_FEED,
            feed_type=self.feed_type,
        )
        self.pending_feed, _ = models.Feed.objects.get_or_create(
            title="Pending",
            feed_url="baz.com/rss/",
            public_url="baz.com/",
            approval_status=models.PENDING_FEED,
            feed_type=self.feed_type,
        )

        for feed in [self.approved_feed, self.denied_feed, self.pending_feed]:
            models.FeedItem.objects.get_or_create(
                feed=feed,
                title="%s Item" % feed.title,
                link=feed.public_url,
                date_modified=datetime.datetime.now(),
                guid=feed.title,
            )

    def test_feed_list_only_approved_and_active(self):
        url = reverse('community-feed-list', kwargs={'feed_type_slug': self.feed_type.slug})
        response = self.client.get(url)
        for item in response.context['object_list']:
            self.assertEqual(models.APPROVED_FEED, item.feed.approval_status)

    def test_management_command_sends_no_email_with_no_pending_feeds(self):
        self.pending_feed.delete()
        call_command('send_pending_approval_email', verbosity=0)
        self.assertEqual(0, len(mail.outbox))

    def test_management_command_sends_email_with_pending_feeds(self):
        call_command('send_pending_approval_email', verbosity=0)

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(mail.outbox[0].to, [self.user.email])


class TestForms(SimpleTestCase):
    def test_rejects_stackoverflow_questions(self):
        form = FeedModelForm({
            'title': 'Asynchronous processing of file upload in Django',
            'feed_url': 'http://stackoverflow.com/questions/11752148/',
            'public_url': 'http://stackoverflow.com/questions/11752148/',
        })
        self.assertEqual(
            form.errors,
            {'feed_url': [
                "Stack Overflow questions tagged with 'django' will appear "
                "here automatically."
            ]}
        )
