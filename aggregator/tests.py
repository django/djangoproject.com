import datetime
from operator import attrgetter
from unittest.mock import MagicMock, patch

import requests_mock
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from docs.models import DocumentRelease
from releases.models import Release

from . import feeds, models
from .forms import FeedModelForm


class AggregatorTests(TestCase):
    @requests_mock.mock()
    def setUp(self, mocker):
        mocker.register_uri("POST", settings.PUSH_HUB, status_code=202)
        # document release necessary to fetch main page
        release, _ = Release.objects.get_or_create(
            version="1.4",
        )
        DocumentRelease.objects.update_or_create(
            release=release,
            lang=settings.DEFAULT_LANGUAGE_CODE,
            defaults={"is_default": True},
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
        self.approved_feed_long_url, _ = models.Feed.objects.get_or_create(
            title="Approved long URL",
            feed_url="www.reddit.com/rss/",
            public_url="https://www.reddit.com/r/django/?param=" + "x" * 511,
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

        for feed in [
            self.approved_feed,
            self.approved_feed_long_url,
            self.denied_feed,
            self.pending_feed,
        ]:
            models.FeedItem.objects.get_or_create(
                feed=feed,
                title="%s Item" % feed.title,
                link=feed.public_url,
                date_modified=datetime.datetime.now(),
                guid=feed.title,
            )

    def test_community_index_number_of_queries(self):
        """Intended to prevent an n+1 issue on the community index view"""
        url = reverse("community-index")
        with self.assertNumQueries(9):
            self.client.get(url)

    def test_empty_feed_type_not_rendered(self):
        empty_type = models.FeedType.objects.create(name="Empty", slug="empty")
        models.Feed.objects.create(
            title="Empty blog",
            feed_url="empty.com/rss/",
            public_url="empty.com/",
            approval_status=models.APPROVED_FEED,
            feed_type=empty_type,
        )
        response = self.client.get(reverse("community-index"))
        self.assertNotContains(response, "Empty")

    def test_feed_list_only_approved_and_active(self):
        url = reverse(
            "community-feed-list", kwargs={"feed_type_slug": self.feed_type.slug}
        )
        response = self.client.get(url)
        for item in response.context["object_list"]:
            self.assertEqual(models.APPROVED_FEED, item.feed.approval_status)

    def test_feed_list_number_of_queries(self):
        url = reverse(
            "community-feed-list", kwargs={"feed_type_slug": self.feed_type.slug}
        )
        with self.assertNumQueries(9):
            self.client.get(url)

    def test_management_command_sends_no_email_with_no_pending_feeds(self):
        self.pending_feed.delete()
        call_command("send_pending_approval_email", verbosity=0)
        self.assertEqual(0, len(mail.outbox))

    def test_management_command_sends_email_with_pending_feeds(self):
        call_command("send_pending_approval_email", verbosity=0)

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_feeditem_approved(self):
        self.assertQuerySetEqual(
            models.FeedItem.objects.approved(),
            ["Approved long URL Item", "Approved Item"],
            transform=attrgetter("title"),
        )

    def test_community_feed_has_only_approved(self):
        feed = feeds.CommunityAggregatorFeed()
        self.assertQuerySetEqual(
            feed.items(self.feed_type),
            ["Approved long URL Item", "Approved Item"],
            transform=attrgetter("title"),
        )

    def test_feedtype_items_has_only_approved(self):
        self.assertQuerySetEqual(
            self.feed_type.items(),
            ["Approved long URL Item", "Approved Item"],
            transform=attrgetter("title"),
        )

    def test_logged_in_user_can_delete_own_feed(self):
        user = User.objects.create_user(
            username="deleter",
            password="pass123",
        )

        feed = models.Feed.objects.create(
            title="My Feed",
            feed_url="https://example.com/rss/",
            public_url="https://example.com/",
            approval_status=models.PENDING_FEED,
            feed_type=self.feed_type,
            owner=user,
        )

        self.client.login(username="deleter", password="pass123")

        response = self.client.post(reverse("community-delete-feed", args=[feed.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(models.Feed.objects.filter(id=feed.id).exists())


class TestForms(SimpleTestCase):
    def test_rejects_stackoverflow_questions(self):
        form = FeedModelForm(
            {
                "title": "Asynchronous processing of file upload in Django",
                "feed_url": "http://stackoverflow.com/questions/11752148/",
                "public_url": "http://stackoverflow.com/questions/11752148/",
            }
        )
        self.assertEqual(
            form.errors,
            {
                "feed_url": [
                    "Stack Overflow questions tagged with 'django' will appear "
                    "here automatically."
                ]
            },
        )


class FeedSubscriptionCleanupTests(TestCase):
    """
    Regression tests for the stale subscription bug related to Issue #1647.

    When an already-approved feed's feed_url is changed, the old Superfeedr
    subscription must be cancelled before the new URL is subscribed. Without
    this cleanup, stale subscriptions accumulate for URLs that no longer
    belong to any feed.
    """

    @requests_mock.mock()
    def setUp(self, mocker):
        mocker.register_uri("POST", settings.PUSH_HUB, status_code=202)
        release, _ = Release.objects.get_or_create(version="1.4")
        DocumentRelease.objects.update_or_create(
            release=release,
            lang=settings.DEFAULT_LANGUAGE_CODE,
            defaults={"is_default": True},
        )
        self.feed_type, _ = models.FeedType.objects.get_or_create(
            name="Subscription Test Feed Type",
            slug="subscription-test-feed-type",
            can_self_add=True,
        )

    @requests_mock.mock()
    def test_changing_approved_feed_url_unsubscribes_old_url(self, mocker):
        """
        When the feed_url of an approved feed is changed, the old subscription
        is removed and a new subscription is created for the updated URL.
        """
        mocker.register_uri("POST", settings.PUSH_HUB, status_code=202)

        feed = models.Feed.objects.create(
            title="Old Feed",
            feed_url="https://oldblog.com/rss/",
            public_url="https://oldblog.com/",
            approval_status=models.APPROVED_FEED,
            feed_type=self.feed_type,
        )

        old_url = "https://oldblog.com/rss/"
        new_url = "https://newblog.com/rss/"

        old_unsubscribe = MagicMock()
        mock_old_subscription = MagicMock()
        mock_old_subscription.unsubscribe = old_unsubscribe

        with (
            patch(
                "aggregator.models.Subscription.objects.get",
                return_value=mock_old_subscription,
            ) as mock_get,
            patch("aggregator.models.Subscription.objects.subscribe") as mock_subscribe,
        ):
            feed.feed_url = new_url
            feed.save()

            # The old URL subscription should have been looked up and cancelled.
            mock_get.assert_called_once_with(topic=old_url)
            old_unsubscribe.assert_called_once()

            # A new subscription should have been created for the new URL.
            mock_subscribe.assert_called_once_with(new_url, settings.PUSH_HUB)

    @requests_mock.mock()
    def test_saving_approved_feed_with_unchanged_url_does_not_unsubscribe(self, mocker):
        """
        When an approved feed is saved without changing feed_url, no
        unnecessary unsubscribe call is made for the existing subscription.
        """
        mocker.register_uri("POST", settings.PUSH_HUB, status_code=202)

        feed = models.Feed.objects.create(
            title="Stable Feed",
            feed_url="https://stableblog.com/rss/",
            public_url="https://stableblog.com/",
            approval_status=models.APPROVED_FEED,
            feed_type=self.feed_type,
        )

        with (
            patch("aggregator.models.Subscription.objects.get") as mock_get,
            patch("aggregator.models.Subscription.objects.subscribe") as mock_subscribe,
        ):
            # Save without changing any field.
            feed.save()

            # get() should NOT be called to look up an old subscription.
            mock_get.assert_not_called()

            # A subscription renewal for the same URL is still expected.
            mock_subscribe.assert_called_once_with(
                "https://stableblog.com/rss/", settings.PUSH_HUB
            )

    @requests_mock.mock()
    def test_new_approved_feed_does_not_trigger_old_unsubscribe(self, mocker):
        """
        When a brand-new feed is saved as approved for the first time (no
        prior database record), no unsubscribe call is attempted.
        """
        mocker.register_uri("POST", settings.PUSH_HUB, status_code=202)

        with (
            patch("aggregator.models.Subscription.objects.get") as mock_get,
            patch("aggregator.models.Subscription.objects.subscribe") as mock_subscribe,
        ):
            models.Feed.objects.create(
                title="Brand New Feed",
                feed_url="https://brand-new.com/rss/",
                public_url="https://brand-new.com/",
                approval_status=models.APPROVED_FEED,
                feed_type=self.feed_type,
            )

            # No old subscription lookup should happen for a new feed.
            mock_get.assert_not_called()

            # The new URL should be subscribed.
            mock_subscribe.assert_called_once_with(
                "https://brand-new.com/rss/", settings.PUSH_HUB
            )
