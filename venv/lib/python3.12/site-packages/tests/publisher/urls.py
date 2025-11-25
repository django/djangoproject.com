from django.urls import include, path

from .feeds import HubFeed, OverrideHubFeed, DynamicHubFeed


urlpatterns = [
    path('feed/', HubFeed(), name='feed'),
    path('override-feed/', OverrideHubFeed(), name='override-feed'),
    path('dynamic-feed/', DynamicHubFeed(), name='dynamic-feed'),
    path('subscriber/', include('django_push.subscriber.urls')),
]
