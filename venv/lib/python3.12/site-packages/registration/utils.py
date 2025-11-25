from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION[0] < 3:
    from django.utils.translation import ugettext_lazy as _  # noqa
else:
    from django.utils.translation import gettext_lazy as _  # noqa
