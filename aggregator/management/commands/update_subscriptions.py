import logging
from datetime import timedelta

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone
from django_push.subscriber.models import Subscription

from ...models import APPROVED_FEED, Feed

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **kwargs):
        feed_urls = set(Feed.objects.filter(
            approval_status=APPROVED_FEED
        ).values_list('feed_url', flat=True))

        subscribed_urls = set(Subscription.objects.values_list('topic',
                                                               flat=True))

        missing_feeds = feed_urls - subscribed_urls
        extra_feeds = subscribed_urls - feed_urls

        for url in missing_feeds:
            logger.info('Subscribing to {0}'.format(url))
            Subscription.objects.subscribe(url, settings.PUSH_HUB)

        for subscription in Subscription.objects.filter(topic__in=extra_feeds):
            logger.info('Unsubscribing from {0} ({1})'.format(
                subscription.pk, subscription.topic))
            subscription.unsubscribe()

        limit = timezone.now() + timedelta(days=2)
        for subscription in Subscription.objects.exclude(
                topic__in=extra_feeds).filter(lease_expiration__lte=limit):
            logger.info('Renewing subscription for {0} ({1})'.format(
                subscription.topic, subscription.pk))
            subscription.subscribe()
