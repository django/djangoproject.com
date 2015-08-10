from django.contrib import admin
from django.db.models import Sum
from sorl.thumbnail.admin import AdminImageMixin

from .models import Campaign, DjangoHero, Donation, Payment, Testimonial


@admin.register(DjangoHero)
class DjangoHeroAdmin(AdminImageMixin, admin.ModelAdmin):
    list_filter = ['approved', 'created', 'modified', 'hero_type', 'is_visible', 'is_subscribed']
    list_display = ['id', 'name', 'email', 'created', 'modified', 'approved', 'hero_type']
    list_editable = ['approved', 'hero_type']
    ordering = ['-created']


class PaymentInline(admin.TabularInline):
    model = Payment


@admin.register(Donation)
class Donation(admin.ModelAdmin):
    raw_id_fields = ['donor']
    list_display = ['id', 'amount', 'donor', 'created', 'modified']
    list_filter = ['created', 'modified']
    ordering = ['-created']
    inlines = [PaymentInline]

    def get_queryset(self, request):
        """Annotate the sum of related payments to every donation."""
        qs = super(Donation, self).get_queryset(request)
        return qs.annotate(amount=Sum('payment__amount'))

    def amount(self, obj):
        # Since amount is an annotated field, it is not recognized as a property
        # of the model for list_display so we need an actual method that
        # references it.
        return obj.amount


@admin.register(Testimonial)
class Testimonial(admin.ModelAdmin):
    pass


@admin.register(Campaign)
class Campaign(admin.ModelAdmin):
    list_display = ['name', 'goal', 'template', 'stretch_goal',
                    'start_date', 'end_date', 'is_active', 'is_public']
    list_filter = ['is_active', 'is_public']
    prepopulated_fields = {'slug': ('name',)}
