from django.urls import path

from .. import views

urlpatterns = [
    path(
        "", views.MeetingArchiveIndex.as_view(), name="foundation_meeting_archive_index"
    )
]
