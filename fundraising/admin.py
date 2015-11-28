from django.contrib import admin
from django.db.models import Sum
from sorl.thumbnail.admin import AdminImageMixin

from .models import Campaign, DjangoHero, Donation, Payment, Testimonial


class DonationInline(admin.TabularInline):
    fields = ['id', 'created', 'interval', 'subscription_amount']
    extra = 0
    model = Donation


@admin.register(DjangoHero)
class DjangoHeroAdmin(AdminImageMixin, admin.ModelAdmin):
    inlines = [DonationInline]
    list_filter = ['approved', 'created', 'modified', 'hero_type', 'is_visible', 'is_subscribed']
    list_display = ['id', 'name', 'email', 'created', 'modified', 'approved', 'hero_type']
    list_editable = ['approved', 'hero_type']
    ordering = ['-created']
    search_fields = ['name', 'email', 'stripe_customer_id']


class PaymentInline(admin.TabularInline):
    extra = 0
    model = Payment


@admin.register(Donation)
class Donation(admin.ModelAdmin):
    raw_id_fields = ['donor']
    list_display = ['id', 'amount', 'donor', 'created', 'modified']
    list_filter = ['created', 'modified']
    ordering = ['-created']
    inlines = [PaymentInline]
    search_fields = ['donor__name', 'donor__email', 'donor__stripe_customer_id']

    def get_queryset(self, request):
        """Annotate the sum of related payments to every donation."""
        qs = super(Donation, self).get_queryset(request)
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


@admin.register(Campaign)
class Campaign(admin.ModelAdmin):
    list_display = ['name', 'goal', 'template', 'stretch_goal',
                    'start_date', 'end_date', 'is_active', 'is_public']
    list_filter = ['is_active', 'is_public']
    prepopulated_fields = {'slug': ('name',)}
