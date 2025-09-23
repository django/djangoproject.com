from django.views import generic

from . import models


class CoreDevelopers(generic.ListView):
    queryset = models.CoreAwardCohort.objects.prefetch_related("recipients").order_by(
        "-cohort_date"
    )
