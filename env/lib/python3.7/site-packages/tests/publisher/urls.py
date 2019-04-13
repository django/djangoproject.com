from django.conf.urls import url, include

from .feeds import HubFeed, OverrideHubFeed, DynamicHubFeed


urlpatterns = [
    url(r'^feed/$', HubFeed(), name='feed'),
    url(r'^override-feed/$', OverrideHubFeed(), name='override-feed'),
    url(r'^dynamic-feed/$', DynamicHubFeed(), name='dynamic-feed'),
    url(r'^subscriber/', include('django_push.subscriber.urls')),
]
