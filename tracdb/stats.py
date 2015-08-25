"""
Various queries for grabbing interesting user stats from Trac.
"""
import operator
from collections import OrderedDict

import django.db

from .models import Attachment, Revision, Ticket, TicketChange

_statfuncs = []


def stat(title):
    """
    Register a function as a "stat"

    The function should take a username and return a number.
    """

    def _inner(f):
        _statfuncs.append(f)
        f.title = title
        return f
    return _inner


def get_user_stats(username):
    stats = OrderedDict()
    for func in sorted(_statfuncs, key=operator.attrgetter('title')):
        stats[func.title] = func(username)
    return stats


@stat('Commits')
def commit_count(username):
    return Revision.objects.filter(author=username).count()


@stat('Tickets closed')
def tickets_closed(username):
    # Raw query so that we can do COUNT(DISTINCT ticket).
    q = """SELECT COUNT(DISTINCT ticket) FROM ticket_change
           WHERE author = %s AND field = 'status' AND newvalue = 'closed';"""
    return run_single_value_query(q, username)


@stat('Tickets opened')
def tickets_opened(username):
    return Ticket.objects.filter(reporter=username).count()


@stat('New tickets reviewed')
def new_tickets_reviewed(username):
    # We don't want to de-dup as for tickets_closed: multiple reviews of the
    # same ticket should "count" as a review.
    qs = TicketChange.objects.filter(author=username, field='stage', oldvalue='Unreviewed')
    qs = qs.exclude(newvalue='Unreviewed')
    return qs.count()


@stat('Patches submitted')
def patches_submitted(username):
    return Attachment.objects.filter(author=username).count()


def run_single_value_query(query, *params):
    """
    Helper: run a query returning a single value (e.g. a COUNT) and return the value.
    """
    c = django.db.connections['trac'].cursor()
    c.execute(query, params)
    return c.fetchone()[0]
