from django.contrib import admin

from .models import APPROVED_FEED, DENIED_FEED, Feed, FeedItem, FeedType


def mark_approved(modeladmin, request, queryset):
    for item in queryset.iterator():
        item.approval_status = APPROVED_FEED
        item.save()


mark_approved.short_description = "Mark selected feeds as approved."


def mark_denied(modeladmin, request, queryset):
    for item in queryset.iterator():
        item.approval_status = DENIED_FEED
        item.save()


mark_denied.short_description = "Mark selected feeds as denied."


admin.site.register(
    Feed,
    list_display=["title", "feed_type", "public_url", "approval_status"],
    list_filter=["feed_type", "approval_status"],
    ordering=["title"],
    search_fields=["title", "public_url"],
    raw_id_fields=['owner'],
    list_editable=["approval_status"],
    list_per_page=500,
    actions=[mark_approved, mark_denied],
)

admin.site.register(
    FeedItem,
    list_display=['title', 'feed', 'date_modified'],
    list_filter=['feed'],
    search_fields=['feed__title', 'feed__public_url', 'title'],
    date_heirarchy=['date_modified'],
)

admin.site.register(
    FeedType,
    prepopulated_fields={'slug': ('name',)},
)
