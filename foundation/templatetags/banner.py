from django import template

from foundation.models import Banner

register = template.Library()


@register.inclusion_tag("foundation/banner.html")
def active_banner():
    return {"banner": Banner.objects.filter(is_active=True).first()}
