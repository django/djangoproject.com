from __future__ import absolute_import

from django.contrib import admin

from .models import Release


class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('version', 'date')
    list_editable = ('date',)

admin.site.register(Release, ReleaseAdmin)
