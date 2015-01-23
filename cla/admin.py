from django.contrib import admin

from .models import ICLA, CCLA, CCLADesignee


class ICLAAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'date_signed']
    raw_id_fields = ['user']
    ordering = ['-date_signed']


class DesigneeInline(admin.StackedInline):
    model = CCLADesignee
    raw_id_fields = ['user']


class CCLAAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'contact_name', 'contact_email', 'date_signed']
    ordering = ['-date_signed']
    inlines = [DesigneeInline]


admin.site.register(ICLA, ICLAAdmin)
admin.site.register(CCLA, CCLAAdmin)
