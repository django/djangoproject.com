import djangodocs.views
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(
        r'^$',
        djangodocs.views.index,
    ),
    url(
        r'^(?P<lang>[a-z-]+)/$',
        djangodocs.views.language,
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/(?P<url>[\w./-]*)$',
        djangodocs.views.document,
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_images/(?P<path>.*)$',
        djangodocs.views.images,
    ),
    url(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_source/(?P<path>.*)$',
        djangodocs.views.source,
    ),
)
