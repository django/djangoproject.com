from django import template

from ..models import Entry


register = template.Library()


@register.inclusion_tag('blog/entry_snippet.html')
def render_latest_blog_entries(num):
    entries = Entry.objects.published()[:num]
    return {
        'entries': entries,
    }


@register.inclusion_tag('blog/month_links_snippet.html')
def render_month_links():
    return {
        'dates': Entry.objects.published().dates('pub_date', 'month', order='DESC'),
    }
