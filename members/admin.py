from django.contrib import admin

from members.models import CorporateMember, DeveloperMember


@admin.register(DeveloperMember)
class DeveloperMemberAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'email',
        'is_active',
        'member_since',
        'member_until',
    )
    search_fields = ('name',)


@admin.register(CorporateMember)
class CorporateMemberAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'is_approved',
        'contact_email',
        'billing_email',
        'membership_level',
        'membership_start',
        'membership_expires',
    )
    list_editable = ('is_approved',)
    search_fields = ('name',)
