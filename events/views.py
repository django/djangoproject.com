from django.db.models import Q
from django.views.generic import TemplateView

from blog.models import Event


class EventListView(TemplateView):
    template_name = "events/events.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        location = self.request.GET.get("location", "").strip()
        year = self.request.GET.get("year", "").strip()

        qs = Event.objects.published()
        if query:
            qs = qs.filter(Q(headline__icontains=query) | Q(location__icontains=query))
        if location:
            qs = qs.filter(location__icontains=location)
        if year and year.isdigit():
            qs = qs.filter(date__year=int(year))

        context["upcoming_events"] = qs.future()
        context["past_events"] = qs.past()
        context["query"] = query
        context["selected_location"] = location
        context["selected_year"] = year

        all_published = Event.objects.published()
        context["locations"] = (
            all_published.values_list("location", flat=True)
            .distinct()
            .order_by("location")
        )
        years = (
            all_published.values_list("date__year", flat=True)
            .distinct()
            .order_by("-date__year")
        )
        context["years"] = [y for y in years if y is not None]
        return context
