from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^weblog/', include('django_website.apps.blog.urls.blog')),
    (r'^documentation/', include('django_website.apps.docs.urls.docs')),
    (r'^comments/', include('django.contrib.comments.urls.comments')),
    (r'^rss/', include('django.conf.urls.rss')),
    (r'', include('django.conf.urls.flatfiles')),
)
