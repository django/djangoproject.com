from .dev import *  # noqa

# django-hosts settings
if parent_host := SECRETS.get("parent_host"):
    PARENT_HOST = parent_host

# debug-toolbar settings
INTERNAL_IPS = SECRETS.get("internal_ips", ["127.0.0.1"])
