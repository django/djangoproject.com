from __future__ import absolute_import

from django.contrib import admin
from .models import Entry

admin.site.register(Entry,
    list_display = ('pub_date', 'headline', 'author'),
)