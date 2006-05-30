from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^password_reset/', include('django.conf.urls.admin_password_reset')),
    (r'^r/', include('django.conf.urls.shortcut')),
    (r'', include('django.contrib.admin.urls.admin')),
)
