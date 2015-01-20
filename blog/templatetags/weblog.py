from django import template

from ..models import Entry


register = template.Library()


@register.inclusion_tag('blog/entry_snippet.html')
def render_latest_blog_entries(num, hide_summary=False, hide_readmore=False):
    entries = Entry.objects.published()[:num]
    return {
        'entries': entries,
        'hide_summary': hide_summary,
        'hide_readmore': hide_readmore,
    }


@register.inclusion_tag('blog/month_links_snippet.html')
def render_month_links():
    return {
        'dates': Entry.objects.published().dates('pub_date', 'month', order='DESC'),
    }
