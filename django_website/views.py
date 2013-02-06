"""
Misc. views.
"""
from __future__ import absolute_import

from django.contrib.comments.models import Comment
from django.contrib.sitemaps import views as sitemap_views
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import requires_csrf_token
from django.views.generic import list_detail

from .sitemaps import FlatPageSitemap, WeblogSitemap

@cache_page(60*60*6)
def sitemap(request):
    return sitemap_views.sitemap(request, sitemaps={
        'weblog': WeblogSitemap,
        'flatpages': FlatPageSitemap,
    })

def comments(request):
    return list_detail.object_list(
        request,
        queryset = Comment.objects.filter(is_public=True).order_by('-submit_date'),
        paginate_by = 30,
    )

@requires_csrf_token
def server_error(request, template_name='500.html'):
    """
    Custom 500 error handler for static stuff.
    """
    return render(request, template_name)
