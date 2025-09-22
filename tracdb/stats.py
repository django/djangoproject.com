"""
Various queries for grabbing interesting user stats from Trac.
"""

import operator
from collections import OrderedDict, namedtuple

from django.conf import settings
from django.db.models import Q

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


def get_user_stats(user):
    stats = OrderedDict()
    for func in sorted(_statfuncs, key=operator.attrgetter("title")):
        stats[func.title] = func(user)
    return stats


@stat("Commits")
def commit_count(user):
    count = Revision.objects.filter(
        Q(author__istartswith=f"{user.username} <")
        | Q(author__istartswith=f"{user.get_full_name()} <")
    ).count()
    # This assumes that the username is their GitHub username.
    link = f"https://github.com/django/django/commits/main/?author={user.username}"
    return StatData(count=count, link=link)


@stat("Tickets fixed")
def tickets_fixed(user):
    query = f"owner={user.username}&resolution=fixed"
    count = Ticket.objects.from_querystring(query).count()
    link = get_trac_link(query)
    return StatData(count=count, link=link)


@stat("Tickets opened")
def tickets_opened(user):
    query = f"reporter={user.username}"
    count = Ticket.objects.from_querystring(query).count()
    link = get_trac_link(query)
    return StatData(count=count, link=link)


@stat("New tickets triaged")
def new_tickets_reviewed(user):
    # We don't want to de-dup as for tickets_closed: multiple reviews of the
    # same ticket should "count" as a review.
    qs = TicketChange.objects.filter(
        author=user.username, field="stage", oldvalue="Unreviewed"
    )
    qs = qs.exclude(newvalue="Unreviewed")
    return StatData(count=qs.count(), link=None)
