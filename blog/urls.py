from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\w-]+)/$',
        views.BlogDateDetailView.as_view()
    ),
    url(
        r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        views.BlogDayArchiveView.as_view()
    ),
    url(
        r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        views.BlogMonthArchiveView.as_view()
    ),
    url(
        r'^(?P<year>\d{4})/$',
        views.BlogYearArchiveView.as_view()
    ),
    url(
        r'^/?$',
        views.BlogArchiveIndexView.as_view(),
        name="blog-index"
    ),
]
