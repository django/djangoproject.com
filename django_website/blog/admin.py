from __future__ import absolute_import

from django.contrib import admin

from .models import Entry

class EntryAdmin(admin.ModelAdmin):
    list_display = ('headline', 'pub_date', 'is_active', 'is_published', 'author')
    list_filter = ('is_active',)
    exclude = ('summary_html', 'body_html')
    prepopulated_fields = {"slug": ("headline",)}

admin.site.register(Entry, EntryAdmin)
