from django.views.generic.dates import (
    ArchiveIndexView, DateDetailView, DayArchiveView, MonthArchiveView,
    YearArchiveView,
)

from .models import Entry, Event


class BlogViewMixin:

    date_field = 'pub_date'
    paginate_by = 10

    def get_allow_future(self):
        return self.request.user.is_staff

    def get_queryset(self):
        if self.request.user.is_staff:
            return Entry.objects.all()
        else:
            return Entry.objects.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        events_queryset = Event.objects.future()
        if not self.request.user.is_staff:
            events_queryset = events_queryset.published()

        context['events'] = events_queryset[:3]

        return context


class BlogArchiveIndexView(BlogViewMixin, ArchiveIndexView):
    pass


class BlogYearArchiveView(BlogViewMixin, YearArchiveView):
    make_object_list = True


class BlogMonthArchiveView(BlogViewMixin, MonthArchiveView):
    pass


class BlogDayArchiveView(BlogViewMixin, DayArchiveView):
    pass


class BlogDateDetailView(BlogViewMixin, DateDetailView):
    pass
