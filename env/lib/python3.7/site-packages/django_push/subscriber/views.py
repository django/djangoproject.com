import hashlib
import hmac
import logging

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from requests.utils import parse_header_links

from .models import Subscription
from .signals import updated

logger = logging.getLogger(__name__)


class CallbackView(generic.View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CallbackView, self).dispatch(*args, **kwargs)

    def get(self, request, pk, *args, **kwargs):
        subscription = get_object_or_404(Subscription, pk=pk)
        params = ['hub.mode', 'hub.topic', 'hub.challenge']
        missing = [p for p in params if p not in request.GET]
        if missing:
            return HttpResponseBadRequest("Missing parameters: {0}".format(
                ", ".join(missing)))

        topic = request.GET['hub.topic']
        if not topic == subscription.topic:
            return HttpResponseBadRequest("Mismatching topic URL")

        mode = request.GET['hub.mode']

        if mode not in ['subscribe', 'unsubscribe', 'denied']:
            return HttpResponseBadRequest("Unrecognized hub.mode parameter")

        if mode == 'subscribe':
            if 'hub.lease_seconds' not in request.GET:
                return HttpResponseBadRequest(
                    "Missing hub.lease_seconds parameter")

            if not request.GET['hub.lease_seconds'].isdigit():
                return HttpResponseBadRequest(
                    "hub.lease_seconds must be an integer")

            seconds = int(request.GET['hub.lease_seconds'])
            subscription.set_expiration(seconds)
            subscription.verified = True
            logger.debug("Verifying subscription for topic {0} via {1} "
                         "(expires in {2}s)".format(subscription.topic,
                                                    subscription.hub,
                                                    seconds))
            Subscription.objects.filter(pk=subscription.pk).update(
                verified=True,
                lease_expiration=subscription.lease_expiration)

        if mode == 'unsubscribe':
            # TODO make sure it was pending deletion
            logger.debug("Deleting subscription for topic {0} via {1}".format(
                subscription.topic, subscription.hub))
            subscription.delete()

        # TODO handle denied subscriptions

        return HttpResponse(request.GET['hub.challenge'])

    def post(self, request, pk, *args, **kwargs):
        subscription = get_object_or_404(Subscription, pk=pk)

        if subscription.secret:
            signature = request.META.get('HTTP_X_HUB_SIGNATURE', None)
            if signature is None:
                logger.debug("Ignoring payload for subscription {0}, missing "
                             "signature".format(subscription.pk))
                return HttpResponse('')

            hasher = hmac.new(subscription.secret.encode('utf-8'),
                              request.body,
                              hashlib.sha1)
            digest = 'sha1=%s' % hasher.hexdigest()
            if signature != digest:
                logger.debug("Mismatching signature for subscription {0}: "
                             "got {1}, expected {2}".format(subscription.pk,
                                                            signature,
                                                            digest))
                return HttpResponse('')

        self.links = None
        if 'HTTP_LINK' in request.META:
            self.links = parse_header_links(request.META['HTTP_LINK'])
        updated.send(sender=subscription, notification=request.body,
                     request=request, links=self.links)
        self.subscription = subscription
        self.handle_subscription()
        return HttpResponse('')

    def handle_subscription(self):
        """Subclasses may implement this"""
        pass


callback = CallbackView.as_view()
