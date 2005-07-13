from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'', include('django.conf.urls.flatfiles')),
)
