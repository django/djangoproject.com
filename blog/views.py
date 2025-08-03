from django.views.generic.dates import (
    ArchiveIndexView,
    DateDetailView,
    DayArchiveView,
    MonthArchiveView,
    YearArchiveView,
)

from .models import Entry, Event


class BlogViewMixin:
    date_field = "pub_date"
    paginate_by = 10
    banner_is_title = True

    def get_allow_future(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return Entry.objects.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        events_queryset = Event.objects.future().published()

        context["events"] = events_queryset[:3]
        context["banner_is_title"] = self.banner_is_title

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
    banner_is_title = False

    def get_queryset(self):
        """Allows staff users with blog write permission to view unpublished entries."""
        if self.request.user.is_staff and self.request.user.has_perm(
            "blog.change_entry"
        ):
            return Entry.objects.all()
        else:
            return super().get_queryset()
