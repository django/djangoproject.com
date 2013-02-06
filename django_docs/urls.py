from django.conf import settings
from django.conf.urls.defaults import *
from haystack.views import search_view_factory

from docs import views

urlpatterns = patterns('',
    url(
        r'^$',
        views.index,
    ),
    url(
        r'^search/$',
        search_view_factory(view_class=views.DocSearchView),
        name = 'document-search'
    ),
    url(
        r'^(?P<lang>[a-z-]+)/$',
        views.language,
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/$',
        views.document,
        {'url': ''},
        name = 'document-index',
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_objects/$',
        views.objects_inventory,
        name = 'objects-inv',
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_images/(?P<path>.*)$',
        views.SphinxStatic('_images'),
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_source/(?P<path>.*)$',
        views.SphinxStatic('_sources'),
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_downloads/(?P<path>.*)$',
        views.SphinxStatic('_downloads'),
    ),
    url(
        r'^(.*)/index/$',
        views.redirect_index,
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/(?P<url>[\w./-]*)/$',
        views.document,
        name = 'document-detail',
    ),
)
