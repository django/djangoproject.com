from django.contrib import admin

from members.models import CorporateMember, DeveloperMember, Invoice


@admin.register(DeveloperMember)
class DeveloperMemberAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'email',
        'is_active',
        'member_since',
        'member_until',
    ]
    search_fields = ['name']


class InvoiceInline(admin.TabularInline):
    model = Invoice


@admin.register(CorporateMember)
class CorporateMemberAdmin(admin.ModelAdmin):
    list_display = [
        'display_name',
        'contact_email',
        'membership_level',
    ]
    list_filter = [
        'membership_level',
    ]
    inlines = [InvoiceInline]
    search_fields = ['name']
