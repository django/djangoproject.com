from django.conf.urls import url

from . import views

app_name = 'weblog'
urlpatterns = [
    url(
        r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\w-]+)/$',
        views.BlogDateDetailView.as_view(),
        name="entry"
    ),
    url(
        r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        views.BlogDayArchiveView.as_view(),
        name="archive-day"
    ),
    url(
        r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        views.BlogMonthArchiveView.as_view(),
        name="archive-month"
    ),
    url(
        r'^(?P<year>\d{4})/$',
        views.BlogYearArchiveView.as_view(),
        name="archive-year"
    ),
    url(
        r'^$',
        views.BlogArchiveIndexView.as_view(),
        name="index"
    ),
]
