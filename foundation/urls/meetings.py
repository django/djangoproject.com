from django.urls import path

from .. import views


urlpatterns = [
    path('',
         views.MeetingArchiveIndex.as_view(),
         name='foundation_meeting_archive_index'),
    path('<int:year>/',
         views.MeetingArchiveYear.as_view(),
         name='foundation_meeting_archive_year'),
    path('<int:year>/<str:month>/',
         views.MeetingArchiveMonth.as_view(),
         name='foundation_meeting_archive_month'),
    path('<int:year>/<str:month>/<int:day>/',
         views.MeetingArchiveDay.as_view(),
         name='foundation_meeting_archive_day'),
    path('<int:year>/<str:month>/<int:day>/<str:slug>/',
         views.MeetingDetail.as_view(),
         name='foundation_meeting_detail'),
]
