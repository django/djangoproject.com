from worldonline_settings.pam.djangoproject import *

PREPEND_WWW = False
TEMPLATE_DIRS = (
    '/home/html/templates/admin.djangoproject.com/',
    '/home/html/templates/shared-admin/',
)
ROOT_URLCONF = 'worldonline_settings.pam.urls.djangoproject_admin'
MIDDLEWARE_CLASSES = (
    'django.middleware.admin.AdminUserRequired',
    'django.middleware.common.CommonMiddleware',
)
ADMIN_FOR = (
    'worldonline_settings.pam.djangoproject',
)
