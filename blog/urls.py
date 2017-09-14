from django.urls import path

from . import views

app_name = 'weblog'
urlpatterns = [
    path(
        '<int:year>/<str:month>/<int:day>/<slug>/',
        views.BlogDateDetailView.as_view(),
        name="entry"
    ),
    path(
        '<int:year>/<str:month>/<int:day>/',
        views.BlogDayArchiveView.as_view(),
        name="archive-day"
    ),
    path(
        '<int:year>/<str:month>/',
        views.BlogMonthArchiveView.as_view(),
        name="archive-month"
    ),
    path(
        '<int:year>/',
        views.BlogYearArchiveView.as_view(),
        name="archive-year"
    ),
    path(
        '',
        views.BlogArchiveIndexView.as_view(),
        name="index"
    ),
]
