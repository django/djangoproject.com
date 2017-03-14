import bleach
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def markdownify(text):
    return mark_safe(
        bleach.clean(
            markdown.markdown(text, output_format='html5'),
            tags=(
                'a', 'abbr', 'acronym', 'b', 'blockquote', 'em', 'i', 'li',
                'ol', 'p', 'sup', 'strong', 'ul',
            ),
        )
    )
