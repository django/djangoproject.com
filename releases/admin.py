from django.contrib import admin

from .models import Release


class ReleaseAdmin(admin.ModelAdmin):
    list_display = (
        'version', 'is_lts', 'date', 'eol_date',
        'major', 'minor', 'micro', 'show_status', 'iteration',
    )
    list_filter = ('status', 'is_lts')
    ordering = ('-major', '-minor', '-micro', '-status', '-iteration')

    def show_status(self, obj):
        return obj.get_status_display()
    show_status.admin_order_field = 'status'
    show_status.short_description = 'status'


admin.site.register(Release, ReleaseAdmin)
