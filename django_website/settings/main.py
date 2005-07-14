SERVER_EMAIL = 'root@pam.servers.ljworld.com'
MANAGERS = (('Wilson Miner','wminer@ljworld.com'),)

DEBUG = True
PREPEND_WWW = True
DATABASE_NAME = 'djangoproject'
SITE_ID = 1
TEMPLATE_DIRS = (
    '/home/html/templates/djangoproject.com/',
    '/home/html/templates/default/',
)
ROOT_URLCONF = 'django_website.settings.urls.main'
INSTALLED_APPS = (
    'django.contrib.comments',
    'django_website.apps.blog',
    'django_website.apps.docs',
)
MEDIA_ROOT = "/home/html/djangoproject.com/m/"
MEDIA_URL = "http://www.djangoproject.com.com/m/"

# setting for documentation root path
DJANGO_DOCUMENT_ROOT_PATH = "/home/html/djangoproject.com/docs/"