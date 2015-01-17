from django.contrib import admin
from .models import DjangoHero


@admin.register(DjangoHero)
class DjangoHeroAdmin(admin.ModelAdmin):
    pass
