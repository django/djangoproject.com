from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin

from .models import Campaign, DjangoHero, Donation, Testimonial


@admin.register(DjangoHero)
class DjangoHeroAdmin(AdminImageMixin, admin.ModelAdmin):
    list_filter = ['approved', 'created', 'modified',
                   'is_visible', 'is_subscribed', 'is_amount_displayed']
    list_display = ['id', 'name', 'email', 'created', 'modified', 'approved']
    list_editable = ['approved']
    ordering = ['-created']


@admin.register(Donation)
class Donation(admin.ModelAdmin):
    raw_id_fields = ['donor']
    list_display = ['id', 'amount', 'donor', 'stripe_charge_id',
                    'created', 'modified', 'campaign_name']
    list_filter = ['campaign_name', 'created', 'modified']
    ordering = ['-created']


@admin.register(Testimonial)
class Testimonial(admin.ModelAdmin):
    pass


@admin.register(Campaign)
class Campaign(admin.ModelAdmin):
    list_display = ['name', 'goal', 'template', 'stretch_goal',
                    'start_date', 'end_date', 'is_active', 'is_public']
    list_filter = ['is_active', 'is_public']
    prepopulated_fields = {'slug': ('name',)}
