from django.contrib import admin
from .models import DjangoHero, Donation, Testimonial


@admin.register(DjangoHero)
class DjangoHeroAdmin(admin.ModelAdmin):
    list_filter = ['approved']


@admin.register(Donation)
class Donation(admin.ModelAdmin):
    raw_id_fields = ['donor']


@admin.register(Testimonial)
class Testimonial(admin.ModelAdmin):
    pass
