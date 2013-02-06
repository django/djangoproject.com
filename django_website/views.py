from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token

@requires_csrf_token
def server_error(request, template_name='500.html'):
    """
    Custom 500 error handler for static stuff.
    """
    return render(request, template_name)
