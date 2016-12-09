from datetime import date, timedelta

from django.contrib import admin
from django.templatetags.static import static
from django.utils.formats import localize
from django.utils.html import format_html

from members.models import CorporateMember, IndividualMember, Invoice


@admin.register(IndividualMember)
class IndividualMemberAdmin(admin.ModelAdmin):
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
        'membership_expires',
        '_is_invoiced',
        '_is_paid',
        'contact_email',
        'membership_level',
        'renewal_link',
    ]
    list_filter = [
        'membership_level',
    ]
    inlines = [InvoiceInline]
    search_fields = ['display_name', 'billing_name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('invoice_set')

    def renewal_link(self, obj):
        return format_html(
            '<a href="{}"><img src="{}" alt="renewal link" />',
            obj.get_renewal_link(),
            static('admin/img/icon-changelink.svg'),
        )

    def membership_expires(self, obj):
        expiry_date = obj.get_expiry_date()
        if expiry_date:
            today = date.today()
            # Expired.
            if expiry_date < today:
                color = 'red'
            # Expires within 30 days.
            elif expiry_date < today + timedelta(days=30):
                color = 'orange'
            # Expires more than 30 days from today.
            else:
                color = 'green'
            expiry_date = format_html(
                '<span style="color: {}">{}</span>',
                color,
                localize(expiry_date),
            )
        return expiry_date
