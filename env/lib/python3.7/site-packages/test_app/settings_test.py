# coding: utf-8
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'registration',
    'test_app',
)

DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = '_'
SITE_ID = 1
ROOT_URLCONF = 'test_app.urls_admin_approval'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ADMINS = (
    ('admin1', 'admin1@mail.server.com'),
    ('admin2', 'admin2@mail.server.com'),
)


REGISTRATION_ADMINS = (
    ('admin1', 'registration_admin1@mail.server.com'),
    ('admin2', 'registration_admin2@mail.server.com'),
)
