from django.urls import path

from . import views

urlpatterns = [
    path(
        '',
        views.index,
        name='community-index'
    ),
    path(
        'mine/',
        views.my_feeds,
        name='community-my-feeds'
    ),
    path(
        '<feed_type_slug>/',
        views.FeedListView.as_view(),
        name='community-feed-list'
    ),
    path(
        'add/<feed_type_slug>/',
        views.add_feed,
        name='community-add-feed'
    ),
    path(
        'edit/<int:feed_id>/',
        views.edit_feed,
        name='community-edit-feed'
    ),
    path(
        'delete/<int:feed_id>',
        views.delete_feed,
        name='community-delete-feed'
    ),
]
