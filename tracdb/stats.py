"""
Various queries for grabbing interesting user stats from Trac.
"""

import operator
from collections import OrderedDict, namedtuple

from django.conf import settings

from .models import Revision, Ticket, TicketChange

_statfuncs = []


StatData = namedtuple("StatData", ["count", "link"])


def get_trac_link(query):
    return f"{settings.TRAC_URL}query?{query}&desc=1&order=changetime"


def stat(title):
    """
    Register a function as a "stat"

    The function should take a username and return a StatData object.
    """

    def _inner(f):
        _statfuncs.append(f)
        f.title = title
        return f

    return _inner


def get_user_stats(username):
    stats = OrderedDict()
    for func in sorted(_statfuncs, key=operator.attrgetter("title")):
        stats[func.title] = func(username)
    return stats


@stat("Commits")
def commit_count(username):
    count = Revision.objects.filter(author=username).count()
    # This assumes that the username is their GitHub username, this is very
    # often the case. If this is incorrect, the GitHub will show no commits.
    link = f"https://github.com/django/django/commits/main/?author={username}"
    return StatData(count=count, link=link)


@stat("Tickets fixed")
def tickets_fixed(username):
    query = f"owner={username}&resolution=fixed"
    count = Ticket.objects.from_querystring(query).count()
    link = get_trac_link(query)
    return StatData(count=count, link=link)


@stat("Tickets opened")
def tickets_opened(username):
    query = f"reporter={username}"
    count = Ticket.objects.from_querystring(query).count()
    link = get_trac_link(query)
    return StatData(count=count, link=link)


@stat("New tickets triaged")
def new_tickets_reviewed(username):
    # We don't want to de-dup as for tickets_closed: multiple reviews of the
    # same ticket should "count" as a review.
    qs = TicketChange.objects.filter(
        author=username, field="stage", oldvalue="Unreviewed"
    )
    qs = qs.exclude(newvalue="Unreviewed")
    return StatData(count=qs.count(), link=None)
