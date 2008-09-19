from django.contrib import admin
from django_website.apps.blog.models import Entry

admin.site.register(Entry,
    list_display = ('pub_date', 'headline', 'author'),
)