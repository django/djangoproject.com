from django.contrib import admin
from .models import DjangoHero, Donation, Testimonial


@admin.register(DjangoHero)
class DjangoHeroAdmin(admin.ModelAdmin):
    list_filter = ['approved', 'created', 'modified',
                   'is_visible', 'is_subscribed', 'is_amount_displayed']
    list_display = ['id', 'name', 'email', 'created', 'modified', 'approved']
    list_editable = ['approved']


@admin.register(Donation)
class Donation(admin.ModelAdmin):
    raw_id_fields = ['donor']
    list_display = ['id', 'amount', 'donor', 'stripe_charge_id',
                    'created', 'modified', 'campaign_name']
    list_filter = ['campaign_name', 'created', 'modified']


@admin.register(Testimonial)
class Testimonial(admin.ModelAdmin):
    pass
