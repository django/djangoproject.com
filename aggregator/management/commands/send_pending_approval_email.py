"""
Send an email to settings.FEED_APPROVERS with the feeds that need to
be manually approved.
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.management import BaseCommand
from django.template import Context, Template

from ...models import PENDING_FEED, Feed


class Command(BaseCommand):

    def handle(self, **kwargs):
        try:
            verbosity = int(kwargs['verbosity'])
        except (KeyError, TypeError, ValueError):
            verbosity = 1

        feeds = Feed.objects.filter(approval_status=PENDING_FEED)
        to_email = [x.email for x in User.objects.filter(groups__name=settings.FEED_APPROVERS_GROUP_NAME)]

        if len(feeds) == 0:
            if verbosity >= 1:
                self.stdout.write("There are no pending feeds. Skipping the email.")
            return

        email = """The following feeds are pending approval:
{% regroup feeds by feed_type as feed_grouping %}{% for group in feed_grouping %}
{{ group.grouper }} {% for feed in group.list %}
 - {{ feed.title }} ( {{ feed.feed_url }} ) {% endfor %}
{% endfor %}

To approve them, visit: {% url 'admin:aggregator_feed_changelist' %}
"""

        message = Template(email).render(Context({'feeds': feeds}))
        if verbosity >= 2:
            self.stdout.write("Pending approval email:\n")
            self.stdout.write(message)

        mail.send_mail("django community feeds pending approval", message,
                       'nobody@djangoproject.com', to_email,
                       fail_silently=False)

        if verbosity >= 1:
            self.stdout.write("Sent pending approval email to: %s" % (', '.join(to_email)))
