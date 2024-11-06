import datetime

from django import db
from django.http import JsonResponse
from django.shortcuts import render

from .models import Ticket, _epoc


def bouncing_tickets(request):
    c = db.connections["trac"].cursor()
    c.execute(
        """SELECT * FROM bouncing_tickets
                 WHERE times_reopened >= 3
                 ORDER BY last_reopen_time DESC"""
    )
    tickets = dictfetchall(c)

    # Fix timestamps. LOLTrac.
    for t in tickets:
        t["last_reopen_time"] = ts2dt(t["last_reopen_time"])

    return render(
        request,
        "tracdb/bouncing_tickets.html",
        {
            "tickets": tickets,
        },
    )


def ts2dt(ts):
    return _epoc + datetime.timedelta(microseconds=ts)


def dictfetchall(cursor):
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]


def miniapi(request):
    """
    Return information about the requestest tickets (JSON)
    """
    # TODO: max size
    # TODO: paginate?
    # TODO: error handling
    pks = request.GET.get("ids")
    tickets = (
        Ticket.objects.filter(pk__in=pks)
        .only("status", "reporter", "resolution", "description")
        .prefetch_related("changes")
    )

    return JsonResponse(
        {
            "tickets": [
                {
                    "id": ticket.pk,
                    "status": ticket.status,
                    "reporter": ticket.reporter,  # TODO: sanitize (emails, ...)
                    "resolution": ticket.resolution,
                    "description": ticket.description,
                    "changes": [
                        {
                            "time": change.time.isoformat(),
                            "author": change.author,  # TODO: sanitize (emails, ...)
                            "field": change.field,
                        }
                        for change in ticket.changes.all()
                    ],
                }
                for ticket in tickets
            ]
        }
    )
