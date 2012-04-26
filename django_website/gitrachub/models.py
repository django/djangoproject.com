import re
import warnings
from django.db import models

# Regexen stolen from Trac, see
# http://trac.edgewall.org/browser/trunk/tracopt/ticket/commit_updater.py#L135
TICKET_PREFIX = re.compile(r'(?:#|(?:ticket|issue|bug)[: ]?)')
TICKET_REFERENCE = re.compile(TICKET_PREFIX.pattern + r'([0-9]+)')
TICKET_COMMAND = re.compile(r'(?P<action>[A-Za-z]*)\s*.?\s*(?P<ticket>%s(?:(?:[, &]*|[ ]?and[ ]?)%s)*)' %
                  (TICKET_REFERENCE.pattern, TICKET_REFERENCE.pattern))

class PullRequestManager(models.Manager):
    def get_or_create_from_github_dict(self, prdict):
        """
        Get or create a PullRequest given a GitHub pull request dict.

        See http://developer.github.com/v3/pulls/ for the format of this dict.

        It's probably unclean to put this in the model. Oh well.
        """
        pr, created = self.get_or_create(number=prdict['number'])
        m = TICKET_REFERENCE.search(prdict['title'] + prdict['body'])
        if m:
            pr.ticket_id = int(m.group(1))
            pr.save()
        else:
            # XXX Couldn't find a ticket; what to do here?
            # Create a new ticket? Fail loudly? Leave a note?
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

    objects = PullRequestManager()
