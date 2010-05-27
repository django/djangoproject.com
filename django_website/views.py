"""
Misc. views.
"""
from __future__ import absolute_import

from django.contrib.comments.models import Comment
from django.contrib.sitemaps import views as sitemap_views
from django.views.decorators.cache import cache_page
from django.views.generic import list_detail
from django.views.generic.simple import direct_to_template
from .sitemaps import FlatPageSitemap, WeblogSitemap

def homepage(request):
    return direct_to_template(request, 'homepage.html')

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