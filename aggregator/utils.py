from django.conf import settings


def push_credentials(hub_url):
    """
    Callback for django_push to get a hub's credentials.

    We always use superfeedr so this is easy.
    """
    return tuple(settings.SUPERFEEDR_CREDS)
