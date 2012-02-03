import logging
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django_push.subscriber import signals as push_signals
from django_push.subscriber.models import Subscription
from django.conf import settings

log = logging.getLogger(__name__)

class FeedType(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    can_self_add = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % (self.name,)

    def items(self):
        return FeedItem.objects.filter(feed__feed_type=self)

STATUS_CHOICES = (
    ('P', 'Pending'),
    ('D', 'Denied'),
    ('A', 'Approved')
)


class Feed(models.Model):
    title = models.CharField(max_length=500)
    feed_url = models.URLField(unique=True, max_length=500)
    public_url = models.URLField(max_length=500)
    is_defunct = models.BooleanField()
    approval_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    feed_type = models.ForeignKey(FeedType)
    owner = models.ForeignKey(User, blank=True, null=True, related_name='owned_feeds')

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        super(Feed, self).save(**kwargs)
        if settings.PRODUCTION and self.approval_status == STATUS_CHOICES[2][0]:
            Subscription.objects.subscribe(self.feed_url, settings.PUSH_HUB)

    def delete(self, **kwargs):
        super(Feed, self).delete(**kwargs)
        if settings.PRODUCTION: # @@@ need to validate what pubsub stuff is actually doing here.
            Subscription.objects.unsubscribe(self.feed_url, settings.PUSH_HUB)

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
            log.debug('Creating entry: %s', guid)
            kwargs['guid'] = guid
            item = self.create(**kwargs)

        else:
            log.debug('Updating entry: %s', guid)

            # Update an existing one.
            kwargs.pop('feed', None)

            # Don't update the date since most feeds get this wrong.
            kwargs.pop('date_modified')

            for k,v in kwargs.items():
                setattr(item, k, v)
            item.save()

        return item

class FeedItem(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=500)
    link = models.URLField(max_length=500)
    summary = models.TextField(blank=True)
    date_modified = models.DateTimeField()
    guid = models.CharField(max_length=500, unique=True, db_index=True)

    objects = FeedItemManager()

    class Meta:
        ordering = ("-date_modified",)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.link

def feed_updated(sender, notification, **kwargs):
    log.debug('Recieved notification on subscription ID %s (%s)', sender.id, sender.topic)
    try:
        feed = Feed.objects.get(feed_url=sender.topic)
    except Feed.DoesNotExist:
        log.error("Subscription ID %s (%s) doesn't have a feed.", sender.id, sender.topic)
        return

    for entry in notification.entries:
        title = entry.title
        try:
            guid = entry.get("id", entry.link)
        except AttributeError:
            log.error("Feed ID %s has an entry ('%s') without a link or guid. Skipping.", feed.id, title)
        link = entry.link or guid

        if hasattr(entry, "summary"):
            content = entry.summary
        elif hasattr(entry, "content"):
            content = entry.content[0].value
        elif hasattr(entry, "description"):
            content = entry.description
        else:
            content = u""

        if entry.has_key('updated_parsed'):
            date_modified = datetime.datetime(*entry.updated_parsed[:6])
        else:
            date_modified = datetime.datetime.now()

        FeedItem.objects.create_or_update_by_guid(guid,
            feed = feed,
            title = title,
            link = link,
            summary = content,
            date_modified = date_modified
        )

push_signals.updated.connect(feed_updated)
