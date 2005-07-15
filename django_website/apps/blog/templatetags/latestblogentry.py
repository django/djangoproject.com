from django.core import template
from django.models.blog import entries

class LatestBlogEntriesNode(template.Node):
    def __init__(self, num, varname):
        self.num, self.varname = num, varname

    def render(self, context):
        context[self.varname] = entries.get_list(limit=self.num)
        return ''

def do_get_latest_blog_entries(parser, token):
    """
    {% get_latest_blog_entries 2 as latest_entries %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError, "'%s' tag takes three arguments" % bits[0]
    if bits[2] != 'as':
        raise template.TemplateSyntaxError, "First argument to '%s' tag must be 'as'" % bits[0]
    return LatestBlogEntryNode(bits[1], bits[3])

template.register_tag('get_latest_blog_entries', do_get_latest_blog_entries)
