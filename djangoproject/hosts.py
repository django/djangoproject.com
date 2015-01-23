from django.conf import settings
from django_hosts import host

host_patterns = [
    host(r'www', settings.ROOT_URLCONF, name='www'),
    host(r'docs', 'djangoproject.urls.docs', name='docs'),
    host(r'dashboard', 'dashboard.urls', name='dashboard'),
]
