from __future__ import absolute_import

from django.contrib import admin
from .models import Feed, FeedItem, FeedType

admin.site.register(Feed, 
    list_display  = ["title", "feed_type", "public_url"],
    list_filter   = ["feed_type", "is_defunct"],
    ordering      = ["title"],
    search_fields = ["title", "public_url"],
    raw_id_fields = ['owner'],
    list_per_page = 500,
)

admin.site.register(FeedItem, 
    list_display   = ['title', 'feed', 'date_modified'],
    list_filter    = ['feed'],
    search_fields  = ['feed__title', 'feed__public_url', 'title'],
    date_heirarchy = ['date_modified'],
)

admin.site.register(FeedType,
    prepopulated_fields = {'slug': ('name',)},
)

# Register an admin for django_push.subscriber - it hasn't got one, and I'd
# like to use it for debugging purposes.
from django_push.subscriber.models import Subscription
admin.site.register(Subscription, 
    list_display = ['topic', 'verified', 'lease_expiration'],
)