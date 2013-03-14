from __future__ import absolute_import

from django.contrib import admin

from .models import Release


class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('version', 'date', 'major', 'minor', 'micro', 'show_status', 'iteration')
    ordering = ('-major', '-minor', '-micro', '-status', '-iteration')

    def show_status(self, obj):
        return obj.get_status_display()
    show_status.admin_order_field = 'status'
    show_status.short_description = 'status'

    # Hack -- disable logging because it crashes on the non-integer pk
    def log_addition(self, request, object): pass
    def log_change(self, request, object, message): pass
    def log_deletion(self, request, object, object_repr): pass

admin.site.register(Release, ReleaseAdmin)
