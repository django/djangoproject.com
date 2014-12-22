from django.views.generic.dates import (
    ArchiveIndexView, YearArchiveView,
    MonthArchiveView, DayArchiveView, DateDetailView,
)

from .models import Entry, Event


class BlogViewMixin(object):

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
        context = super(BlogViewMixin, self).get_context_data(**kwargs)

        if self.request.user.is_staff:
            context['events'] = Event.objects.all()[:3]
        else:
            context['events'] = Event.objects.published()[:3]

        return context

class BlogArchiveIndexView(BlogViewMixin, ArchiveIndexView):
    pass


class BlogYearArchiveView(BlogViewMixin, YearArchiveView):
    pass


class BlogMonthArchiveView(BlogViewMixin, MonthArchiveView):
    pass


class BlogDayArchiveView(BlogViewMixin, DayArchiveView):
    pass


class BlogDateDetailView(BlogViewMixin, DateDetailView):
    pass
