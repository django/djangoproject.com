from django.contrib import admin

from .models import DocumentRelease

admin.site.register(
    DocumentRelease,
    list_display=['release', 'lang', 'is_default'],
    list_editable=['is_default'],
    list_filter=['lang'],
)
