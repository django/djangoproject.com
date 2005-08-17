from django_website.settings.main import *

PREPEND_WWW = False
TEMPLATE_DIRS = (
    '/home/html/templates/admin.djangoproject.com/',
    '/home/html/templates/shared-admin/',
)
ROOT_URLCONF = 'django_website.settings.urls.admin'
MIDDLEWARE_CLASSES = (
    'django.middleware.sessions.SessionMiddleware',
    'django.middleware.admin.AdminUserRequired',
    'django.middleware.common.CommonMiddleware',
)
ADMIN_FOR = (
    'django_website.settings.main',
)
