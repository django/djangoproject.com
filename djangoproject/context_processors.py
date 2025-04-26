from django.conf import settings


def display_preview_banner(request):
    """
    Determines if a banner should be displayed to help the website teams
    distinguish between the preview and production sites. The banner is
    based on the domain name configured in settings, if any, and will
    appear on https://*.preview.djangoproject.com/ (but not
    https://*.djangoproject.com/).
    """
    domain_name = getattr(settings, "DOMAIN_NAME", "djangoproject.com")
    return {
        "DISPLAY_PREVIEW_BANNER": domain_name != "djangoproject.com",
    }
