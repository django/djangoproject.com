"""
Send an email to settings.FEED_APPROVERS with the feeds that need to
be manually approved.
"""
from __future__ import absolute_import

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import NoArgsCommand
from django.template import Context, Template
from ...models import Feed, PENDING_FEED

class Command(NoArgsCommand):

    def handle_noargs(self, **kwargs):
        try:
            verbosity = int(kwargs['verbosity'])
        except (KeyError, TypeError, ValueError):
            verbosity = 1

        feeds = Feed.objects.filter(approval_status=PENDING_FEED)

        if len(feeds) == 0:
            if verbosity >= 1:
                print "There are no pending feeds. Skipping the email."
            return

        email = """The following feeds are pending approval:
{% regroup feeds by feed_type as feed_grouping %}{% for group in feed_grouping %}
{{ group.grouper }} {% for feed in group.list %}
 - {{ feed.title }} ( {{ feed.feed_url }} ) {% endfor %}
{% endfor %}

To approve them, visit: http://djangoproject.com{% url admin:aggregator_feed_changelist %}
"""

        message = Template(email).render(Context({'feeds': feeds}))
        if verbosity >= 2:
            print "Pending approval email:\n"
            print message

        send_mail("django community feeds pending approval", message,
                  'nobody@djangoproject.com', settings.FEED_APPROVERS)

        if verbosity >= 1:
            print "Sent pending approval email to: %s" % (', '.join(settings.FEED_APPROVERS))
