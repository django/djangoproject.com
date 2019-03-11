from django.urls import path

from .views import BoardMinutesRecordListView, BoardMinutesDetailView

urlpatterns = [
    path('records/minutes/', BoardMinutesRecordListView.as_view(), name='board-minutes-list'),
    path('records/minutes/<slug>/', BoardMinutesDetailView.as_view(), name='board-minutes-detail')
]
