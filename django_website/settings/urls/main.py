from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^weblog/', include('django_website.apps.blog.urls.blog')),
    (r'', include('django.conf.urls.flatfiles')),
)
