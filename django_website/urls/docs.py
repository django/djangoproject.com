from django.conf import settings
from django.conf.urls.defaults import *
from ..docs import views

urlpatterns = patterns('',
    url(
        r'^$',
        views.index,
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
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/search/$',
        views.search,
        name = 'document-search',
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_objects/$',
        views.objects_inventory,
        name = 'objects-inv',
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_images/(?P<path>.*)$',
        views.images,
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_source/(?P<path>.*)$',
        views.source,
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/(?P<url>[\w./-]*)/$',
        views.document,
        name = 'document-detail',
    ),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$',
            'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
    )