from django.contrib import admin
from django.db.models import Sum
from sorl.thumbnail.admin import AdminImageMixin

from .admin_views import download_donor_report
from .models import DjangoHero, Donation, InKindDonor, Payment, Testimonial


class DonatedFilter(admin.DateFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = 'donation date'


class DonationInline(admin.TabularInline):
    fields = ['id', 'created', 'interval', 'subscription_amount']
    extra = 0
    model = Donation


@admin.register(DjangoHero)
class DjangoHeroAdmin(AdminImageMixin, admin.ModelAdmin):
    actions = [download_donor_report]
    inlines = [DonationInline]
    list_filter = [
        'approved', 'created', 'modified', 'hero_type', 'is_visible',
        'is_subscribed', ('donation__created', DonatedFilter),
    ]
    list_display = ['id', 'name', 'email', 'created', 'modified', 'approved', 'hero_type']
    list_editable = ['approved', 'hero_type']
    ordering = ['-created']
    search_fields = ['name', 'email', 'stripe_customer_id']


class PaymentInline(admin.TabularInline):
    readonly_fields = ['date']
    extra = 0
    model = Payment


@admin.register(Donation)
class Donation(admin.ModelAdmin):
    raw_id_fields = ['donor']
    list_display = ['id', 'amount', 'donor', 'created', 'modified', 'is_active']
    list_filter = ['created', 'modified', 'interval']
    ordering = ['-created']
    inlines = [PaymentInline]
    search_fields = ['donor__name', 'donor__email', 'donor__stripe_customer_id']

    def get_queryset(self, request):
        """Annotate the sum of related payments to every donation."""
        qs = super().get_queryset(request)
        return qs.annotate(amount=Sum('payment__amount'))

    def amount(self, obj):
        # Since amount is an annotated field, it is not recognized as a property
        # of the model for list_display so we need an actual method that
        # references it.
        return obj.amount


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'stripe_charge_id', 'date', 'donation')
    list_select_related = ('donation__donor',)
    ordering = ['-date']
    raw_id_fields = ('donation',)
    search_fields = [
        'stripe_charge_id',
        'donation__donor__name',
        'donation__donor__email',
        'donation__donor__stripe_customer_id',
    ]


@admin.register(Testimonial)
class Testimonial(admin.ModelAdmin):
    pass


admin.site.register(InKindDonor)
