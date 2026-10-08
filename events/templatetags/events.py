from django import template

from blog.models import Event

register = template.Library()


@register.inclusion_tag("events/upcoming_events_snippet.html")
def render_upcoming_events(count=3):
    events = Event.objects.published().future()[:count]
    return {"events": events}
