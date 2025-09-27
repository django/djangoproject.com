from datetime import datetime

from django.http import Http404
from django.shortcuts import redirect
from django.views import generic

from . import models
from . import redirects


class CoreDevelopers(generic.ListView):
    queryset = models.CoreAwardCohort.objects.prefetch_related("recipients").order_by(
        "-cohort_date"
    )


def minutes_redirect(request, year, month, day, slug):
    minutes_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%b-%d").date()
    year, month, day = minutes_date.timetuple()[:3]
    if (year, month, day) not in redirects.MINUTES_DATES:
        raise Http404
    return redirect(
        f"{redirects.MINUTES_BASE_URL}{year}/{year}-{month:02}-{day:02}.md",
        permanent=True,
    )
