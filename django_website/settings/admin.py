from django_website.settings.main import *

PREPEND_WWW = False
TEMPLATE_DIRS = (
    '/home/html/templates/admin.djangoproject.com/',
#    '/home/html/templates/shared-admin/',
)
INSTALLED_APPS = INSTALLED_APPS + ('django.contrib.admin',)
ROOT_URLCONF = 'django_website.settings.urls.admin'
MIDDLEWARE_CLASSES = (
    'django.middleware.sessions.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
)
ADMIN_FOR = (
    'django_website.settings.main',
)
ADMIN_MEDIA_PREFIX = '/m/'
TEMPLATE_LOADERS = (
    'django.core.template.loaders.filesystem.load_template_source',
    'django.core.template.loaders.app_directories.load_template_source',
)
