from django.contrib import admin
from members.models import CorporateMember, DeveloperMember


@admin.register(DeveloperMember)
class DeveloperMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active', 'member_since', 'member_until',)
    search_fields = ('name',)


@admin.register(CorporateMember)
class CorporateMemberAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'contact_email', 'billing_email', 'membership_level',
                    'membership_start', 'membership_expires',)
    search_fields = ('name',)
