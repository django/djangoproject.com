from django.contrib import admin

from . import models


class CoreAwardAdmin(admin.ModelAdmin):
    list_display = ["recipient", "cohort"]


admin.site.register(models.CoreAward, CoreAwardAdmin)
admin.site.register(models.CoreAwardCohort)
