# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from datetime import timedelta

try:
    from urllib.parse import urlparse
except ImportError:  # python2
    from urlparse import urlparse

import requests

from django.conf import settings
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .utils import get_hub_credentials, generate_random_string, get_domain

logger = logging.getLogger(__name__)


class SubscriptionError(Exception):
    pass


class SubscriptionManager(models.Manager):
    def subscribe(self, topic, hub, lease_seconds=None):
        # Only use a secret over HTTPS
        scheme = urlparse(hub).scheme
        defaults = {}
        if scheme == 'https':
            defaults['secret'] = generate_random_string()

        subscription, created = self.get_or_create(hub=hub, topic=topic,
                                                   defaults=defaults)

        # If this code runs in a @transaction.atomic block and the Subscription
        # object is created above, it isn't available until the transaction
        # commits. At that point, it's safe to send a subscription request
        # which then pings back to the the Subscription object.
        def subscribe():
            subscription.subscribe(lease_seconds=lease_seconds)

        transaction.on_commit(subscribe)
        return subscription


class Subscription(models.Model):
    hub = models.URLField(_('Hub'), max_length=1023)
    topic = models.URLField(_('Topic'), max_length=1023)
    verified = models.BooleanField(_('Verified'), default=False)
    verify_token = models.CharField(_('Verify Token'), max_length=255,
                                    blank=True)
    lease_expiration = models.DateTimeField(_('Lease expiration'),
                                            null=True, blank=True)
    secret = models.CharField(_('Secret'), max_length=255, blank=True)

    objects = SubscriptionManager()

    def __unicode__(self):
        return '%s: %s' % (self.topic, self.hub)

    def set_expiration(self, seconds):
        self.lease_expiration = timezone.now() + timedelta(seconds=seconds)

    def has_expired(self):
        if self.lease_expiration:
            return timezone.now() > self.lease_expiration
        return False
    has_expired.boolean = True

    def truncated_topic(self):
        if len(self.topic) > 50:
            return self.topic[:49] + '…'
        return self.topic
    truncated_topic.short_description = _('Topic')
    truncated_topic.admin_order_field = 'topic'

    @property
    def callback_url(self):
        callback_url = reverse('subscriber_callback', args=[self.pk])
        use_ssl = getattr(settings, 'PUSH_SSL_CALLBACK', False)
        scheme = 'https' if use_ssl else 'http'
        return '%s://%s%s' % (scheme, get_domain(), callback_url)

    def subscribe(self, lease_seconds=None):
        return self.send_request(mode='subscribe', lease_seconds=lease_seconds)

    def unsubscribe(self):
        return self.send_request(mode='unsubscribe')

    def send_request(self, mode, lease_seconds=None):
        params = {
            'hub.mode': mode,
            'hub.callback': self.callback_url,
            'hub.topic': self.topic,
            'hub.verify': ['sync', 'async'],
        }

        if self.secret:
            params['hub.secret'] = self.secret

        if lease_seconds is None:
            lease_seconds = getattr(settings, 'PUSH_LEASE_SECONDS', None)

        # If not provided, let the hub decide.
        if lease_seconds is not None:
            params['hub.lease_seconds'] = lease_seconds

        credentials = get_hub_credentials(self.hub)
        timeout = getattr(settings, 'PUSH_TIMEOUT', None)
        response = requests.post(self.hub, data=params, auth=credentials,
                                 timeout=timeout)

        if response.status_code in (202, 204):
            if (
                mode == 'subscribe' and
                response.status_code == 204  # synchronous verification (0.3)
            ):
                self.verified = True
                Subscription.objects.filter(pk=self.pk).update(verified=True)

            elif response.status_code == 202:
                if mode == 'unsubscribe':
                    self.pending_unsubscription = True
                    # TODO check for making sure unsubscriptions are legit
                    # Subscription.objects.filter(pk=self.pk).update(
                    #    pending_unsubscription=True)
            return response

        raise SubscriptionError(
            "Error during request to hub {0} for topic {1}: {2}".format(
                self.hub, self.topic, response.text),
            self,
            response,
        )
