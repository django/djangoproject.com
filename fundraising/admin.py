from django.contrib import admin
from .models import DjangoHero, Donation


@admin.register(DjangoHero)
class DjangoHeroAdmin(admin.ModelAdmin):
    pass


@admin.register(Donation)
class Donation(admin.ModelAdmin):
    raw_id_fields = ['donor']
