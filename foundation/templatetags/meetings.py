from django import template

from ..models import Meeting

register = template.Library()


@register.inclusion_tag("foundation/meeting_snippet.html")
def render_latest_meeting_minute_entries(num):
    meetings = Meeting.objects.order_by("-date").prefetch_related("business")[:num]
    return {"meetings": meetings}
