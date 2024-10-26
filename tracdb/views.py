from django import db
from django.shortcuts import render

from .tractime import timestamp_to_datetime


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
        t["last_reopen_time"] = timestamp_to_datetime(t["last_reopen_time"])

    return render(
        request,
        "tracdb/bouncing_tickets.html",
        {
            "tickets": tickets,
        },
    )


def dictfetchall(cursor):
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
