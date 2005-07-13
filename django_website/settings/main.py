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
ROOT_URLCONF = 'worldonline_settings.pam.urls.djangoproject'
INSTALLED_APPS = (
)
MEDIA_ROOT = "/home/html/djangoproject.com/m/"
MEDIA_URL = "http://www.djangoproject.com.com/m/"
