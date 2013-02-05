from django import template
from django.http import HttpResponseGone

def gone(request, *args, **kwargs):
    """
    Display a nice 410 gone page.
    """
    t = template.loader.get_template('410.html')
    c = template.RequestContext(request, {'request': request})
    return HttpResponseGone(t.render(c))