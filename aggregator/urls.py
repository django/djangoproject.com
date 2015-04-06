from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^$',
        views.index,
        name='community-index'
    ),
    url(
        r'^mine/$',
        views.my_feeds,
        name='community-my-feeds'
    ),
    url(
        r'^(?P<feed_type_slug>[-\w]+)/$',
        views.FeedListView.as_view(),
        name='community-feed-list'
    ),
    url(
        r'^add/(?P<feed_type_slug>[-\w]+)/$',
        views.add_feed,
        name='community-add-feed'
    ),
    url(
        r'^edit/(?P<feed_id>\d+)/$',
        views.edit_feed,
        name='community-edit-feed'
    ),
    url(
        r'^delete/(?P<feed_id>\d+)/$',
        views.delete_feed,
        name='community-delete-feed'
    ),
]
