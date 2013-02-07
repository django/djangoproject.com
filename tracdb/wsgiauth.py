# WSGI auth handlers for Trac

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_www.settings'

from django import db
from django.contrib.auth.models import User

def check_password(environ, user, password):
    try:
        user = User.objects.get(username=user, is_active=True)
        if user.check_password(password):
            return True
        return False
    except User.DoesNotExist:
        return None
    finally:
        db.connection.close()

def groups_for_user(environ, user):
    try:
        u = User.objects.get(username=user)
    except User.DoesNotExist:
        return []
    return [g.name.lower() for g in u.groups.all()]
