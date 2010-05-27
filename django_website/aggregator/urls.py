from __future__ import absolute_import

from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('', 
    url(r'^$', 
        views.index,
        name = 'community-index'
    ),
    url(
        r'^(?P<feed_type_slug>[-\w]+)/$',
        views.feed_list,
        name = "community-feed-list"
    ),
    url(
        r'^add/$',
        views.feed_type_list,
        name = "community-add-feed-list"
    ),
    url(
        r'^add/(?P<feed_type_slug>[-\w]+)/$',
        views.add_feed,
        name = 'community-add-feed'
    ),
)

