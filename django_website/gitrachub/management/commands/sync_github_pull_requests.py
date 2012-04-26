"""
Pull down all open pull requests and attempt to sync them with tickets.
"""

import hashlib
import optparse
from django.conf import settings
from django.core import urlresolvers
from django.core.management.base import NoArgsCommand
from ... import github
from ...models import PullRequest

class Command(NoArgsCommand):
    help = __doc__.strip()

    def handle_noargs(self, **options):
        with github.session() as gh:
            next = 'repos/django/django/pulls'
            while next:
                response = gh.get(next)
                for pr in response.json:
                    pr, created = PullRequest.objects.get_or_create_from_github_dict(pr)
                    print "%s PR %s -> %s" % ("Created" if created else "Updated", pr.number, pr.ticket_id)
                next = response.links.get('next', None)
