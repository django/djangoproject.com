from django.core import template
from django.models.blog import entries

class LatestBlogEntryNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        try:
            e = entries.get_latest()
        except entries.EntryDoesNotExist:
            e = None
        context[self.varname] = e
        return ''

def do_get_latest_blog_entry(parser, token):
    """
    {% get_latest_blog_entry as latest_entry %}
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError, "'%s' tag takes two arguments" % bits[0]
    if bits[1] != 'as':
        raise template.TemplateSyntaxError, "First argument to '%s' tag must be 'as'" % bits[0]
    return LatestBlogEntryNode(bits[2])

template.register_tag('get_latest_blog_entry', do_get_latest_blog_entry)
