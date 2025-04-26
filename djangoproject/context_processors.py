from django.conf import settings


def display_preview_banner(request):
    """
    Determines if a banner should be displayed to help the website teams
    distinguish between the preview and production sites. The banner is
    based on the domain name configured in settings, if any, and will
    appear on https://*.preview.djangoproject.com/ (but not
    https://*.djangoproject.com/ nor in local development).
    """
    production_tld = "djangoproject.com"
    # Note: DOMAIN_NAME is not defined in local development
    domain_name = getattr(settings, "DOMAIN_NAME", production_tld)
    return {
        "DISPLAY_PREVIEW_BANNER": domain_name != production_tld,
    }
