from django.contrib import admin

from .models import Entry, Event


class EntryAdmin(admin.ModelAdmin):
    list_display = ('headline', 'pub_date', 'is_active', 'is_published', 'author')
    list_filter = ('is_active',)
    exclude = ('summary_html', 'body_html')
    prepopulated_fields = {"slug": ("headline",)}

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'body':
            formfield.widget.attrs.update({
                'rows': 60,
                'style': 'font-family: monospace; width: 810px;',
            })
        return formfield


class EventAdmin(admin.ModelAdmin):
    list_display = ('headline', 'external_url', 'date', 'location', 'pub_date', 'is_active', 'is_published')
    list_filter = ('is_active',)


admin.site.register(Entry, EntryAdmin)
admin.site.register(Event, EventAdmin)
