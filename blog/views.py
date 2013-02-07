from django.views.generic.dates import (ArchiveIndexView, YearArchiveView,
    MonthArchiveView, DayArchiveView, DateDetailView)

from .models import Entry

class BlogViewMixin(object):

    date_field = 'pub_date'

    def get_allow_future(self):
        return self.request.user.is_staff

    def get_queryset(self):
        if self.request.user.is_staff:
            return Entry.objects.all()
        else:
            return Entry.objects.published()

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
