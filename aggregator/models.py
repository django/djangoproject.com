import datetime
import logging

import feedparser
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_push.subscriber import signals as push_signals
from django_push.subscriber.models import Subscription

log = logging.getLogger(__name__)


class FeedType(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    can_self_add = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

    def items(self):
        return (
            FeedItem.objects.approved()
            .filter(feed__feed_type=self)
            .select_related("feed", "feed__feed_type")
        )


APPROVED_FEED = "A"
DENIED_FEED = "D"
PENDING_FEED = "P"

STATUS_CHOICES = (
    (PENDING_FEED, _("Pending")),
    (DENIED_FEED, _("Denied")),
    (APPROVED_FEED, _("Approved")),
)


class Feed(models.Model):
    title = models.CharField(max_length=500)
    feed_url = models.URLField(unique=True, max_length=500)
    public_url = models.URLField(max_length=1023)
    approval_status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=PENDING_FEED
    )
    feed_type = models.ForeignKey(FeedType, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name="owned_feeds",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        super().save(**kwargs)
        if settings.SUPERFEEDR_CREDS is not None:
            if self.approval_status == APPROVED_FEED:
                Subscription.objects.subscribe(self.feed_url, settings.PUSH_HUB)
            elif self.approval_status == DENIED_FEED:
                self.unsubscribe()

    def delete(self, **kwargs):
        super().delete(**kwargs)
        if settings.SUPERFEEDR_CREDS is not None:
            self.unsubscribe()

    def unsubscribe(self):
        try:
            Subscription.objects.get(topic=self.feed_url).unsubscribe()
        except Subscription.DoesNotExist:
            pass


class FeedItemManager(models.Manager):
    def create_or_update_by_guid(self, guid, **kwargs):
        """
        Look up a FeedItem by GUID, updating it if it exists, and creating
        it if it doesn't.

        We don't limit it by feed because an item could be in another feed if
        some feeds are themselves aggregators. That's also why we don't update
        the feed field if the feed item already exists.

        Returns (item, created) like get_or_create().
        """
        try:
            item = self.get(guid=guid)

        except self.model.DoesNotExist:
            # Create a new item
            log.debug("Creating entry: %s", guid)
            kwargs["guid"] = guid
            item = self.create(**kwargs)

        else:
            log.debug("Updating entry: %s", guid)

            # Update an existing one.
            kwargs.pop("feed", None)

            # Don't update the date since most feeds get this wrong.
            kwargs.pop("date_modified")

            for k, v in kwargs.items():
                setattr(item, k, v)
            item.save()

        return item

    def approved(self):
        return self.filter(feed__approval_status=APPROVED_FEED)


class FeedItem(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    link = models.URLField(max_length=1023)
    summary = models.TextField(blank=True)
    date_modified = models.DateTimeField()
    guid = models.CharField(max_length=500, unique=True, db_index=True)

    objects = FeedItemManager()

    class Meta:
        ordering = ("-date_modified",)
        indexes = (models.Index(fields=["-date_modified"]),)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return self.link


def feed_updated(sender, notification, **kwargs):
    log.debug(
        "Received notification on subscription ID %s (%s)", sender.id, sender.topic
    )
    try:
        feed = Feed.objects.get(feed_url=sender.topic)
    except Feed.DoesNotExist:
        log.error(
            "Subscription ID %s (%s) doesn't have a feed.", sender.id, sender.topic
        )
        return

    notification = feedparser.parse(notification)

    for entry in notification.entries:
        title = entry.title
        try:
            guid = entry.get("id", entry.link)
        except AttributeError:
            log.error(
                "Feed ID %s has an entry ('%s') without a link or guid. Skipping.",
                feed.id,
                title,
            )
        link = getattr(entry, "link", guid)

        content = ""
        if hasattr(entry, "summary"):
            content = entry.summary

        if hasattr(entry, "description"):
            content = entry.description

        # 'content' takes precedence on anything else. 'summary' and
        # 'description' are usually truncated so it's safe to overwrite them
        if hasattr(entry, "content"):
            content = ""
            for item in entry.content:
                content += item.value

        if "published_parsed" in entry and entry.published_parsed is not None:
            date_modified = datetime.datetime(*entry.published_parsed[:6])
        elif "updated_parsed" in entry and entry.updated_parsed is not None:
            date_modified = datetime.datetime(*entry.updated_parsed[:6])
        else:
            date_modified = datetime.datetime.now()

        FeedItem.objects.create_or_update_by_guid(
            guid,
            feed=feed,
            title=title,
            link=link,
            summary=content,
            date_modified=date_modified,
        )


push_signals.updated.connect(feed_updated)

CONTINENTS = [
    ("Africa", _("Africa")),
    ("North America", _("North America")),
    ("South America", _("South America")),
    ("Europe", _("Europe")),
    ("Asia", _("Asia")),
    ("Oceania", _("Oceania")),
    ("Antarctica", _("Antarctica")),
]


class LocalDjangoCommunity(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    slug = models.SlugField(max_length=125)
    city = models.CharField(max_length=85)
    country = CountryField()
    continent = models.CharField(choices=CONTINENTS, max_length=15)
    website_url = models.URLField(max_length=250, default=None, blank=True, null=True)
    event_site_url = models.URLField(
        max_length=250, default=None, blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _("Local Django Communities")
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(website_url__isnull=False, event_site_url__isnull=False)
                    | models.Q(website_url__isnull=True, event_site_url__isnull=False)
                    | models.Q(website_url__isnull=False, event_site_url__isnull=True)
                ),
                name="website_url_and_or_event_site_url",
            ),
        ]

    def clean(self):
        if not self.website_url and not self.event_site_url:
            raise ValidationError(
                "You must provide at least a website or event site URL"
            )

    def __str__(self):
        return self.name
