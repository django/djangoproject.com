import re
from django.db import models
from ..trac.models import Ticket

# Regexen stolen from Trac, see
# http://trac.edgewall.org/browser/trunk/tracopt/ticket/commit_updater.py#L135
TICKET_PREFIX = re.compile(r'(?:#|(?:ticket|issue|bug)[: ]?)')
TICKET_REFERENCE = re.compile(TICKET_PREFIX.pattern + r'([0-9]+)')
TICKET_COMMAND = re.compile(r'(?P<action>[A-Za-z]*)\s*.?\s*(?P<ticket>%s(?:(?:[, &]*|[ ]?and[ ]?)%s)*)' %
                  (TICKET_REFERENCE.pattern, TICKET_REFERENCE.pattern))

class PullRequestManager(models.Manager):
    def get_or_create_from_github_dict(self, prdict, create_ticket=False):
        """
        Get or create a PullRequest given a GitHub pull request dict.

        See http://developer.github.com/v3/pulls/ for the format of this dict.

        If `create_ticket` is True, a new ticket will be created for this
        pull request if it's not already linked. Otherwise, no ticket will
        be created.

        It's probably unclean to put this in the model. Oh well.
        """
        pr, created = self.get_or_create(number=prdict['number'], defaults={'title': prdict['title']})
        m = TICKET_REFERENCE.search(prdict['title'] + prdict['body'])
        if m:
            try:
                Ticket.objects.get(id=m.group(1))
            except Ticket.DoesNotExist:
                # Oops, an invalid ticket ID. Fall through to below.
                pass
            else:
                pr.ticket_id = int(m.group(1))
                pr.save()
                return pr, created

        # No ticket found in the passed dict, so create a new ticket if needed.
        if create_ticket:
            # XXX figure out the "right" way of creating a new ticket here -
            # ideally we'd preserve authorship, but then how to match github
            # author to trac author?
            pass
        return pr, created

class PullRequest(models.Model):
    """
    A GitHub pull request.
    """
    # The pull request number - using this isntead of "id" to more closely
    # match the GitHub terminology.
    number = models.PositiveIntegerField(primary_key=True)

    # Can't use an FK to ticket 'cause this lives in a different database
    # from trac. So we fake it
    ticket_id = models.PositiveIntegerField(blank=True, null=True, db_index=True)

    # This is available via GitHub's API, but we store a copy locally
    # for ease of use and speed.
    title = models.CharField(max_length=500, blank=True)

    objects = PullRequestManager()
