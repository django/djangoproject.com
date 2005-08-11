from django.core import template
from django.models.aggregator import feeds

class FeedListNode(template.Node):
    def __init__(self, varname):
        self.varname = varname
        
    def render(self, context):
        context[self.varname] = feeds.get_list(is_defunct__exact=False)
        return ''
        
def do_get_feed_list(parser, token):
    """
    {% get_feed_list as feed_list %}
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError, "'%s' tag takes two arguments" % bits[0]
    if bits[1] != "as":
        raise template.TemplateSyntaxError, "First argument to '%s' tag must be 'as'" % bits[0]
    return FeedListNode(bits[2])
    
template.register_tag('get_feed_list', do_get_feed_list)
