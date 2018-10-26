from django.urls import path, re_path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', views.index, name='homepage'),
    path('search/', views.redirect_search),
    path('<lang>/', views.language),
    re_path(
        r'^[a-z-]+/[\w.-]+/internals/team/$',
        RedirectView.as_view(
            url='https://www.djangoproject.com/foundation/teams/',
            permanent=True,
        )
    ),
    re_path('^(?P<lang>[a-z-]+)/(?P<version>stable)/(?P<url>.*)$', views.stable),
    re_path(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/$', views.document,
        {'url': ''}, name='document-index',
    ),
    re_path(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_objects/$',
        views.objects_inventory, name='objects-inv',
    ),
    re_path(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_images/(?P<path>.*)$',
        views.sphinx_static, {'subpath': '_images'}, name='sphinx-images',
    ),
    re_path(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_source/(?P<path>.*)$',
        views.sphinx_static, {'subpath': '_sources'}, name='sphinx-sources',
    ),
    re_path(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_downloads/(?P<path>.*)$',
        views.sphinx_static, {'subpath': '_downloads'}, name='sphinx-downloads',
    ),
    re_path('^(.*)/index/$', views.redirect_index),
    re_path(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/search/$',
        views.search_results, name='document-search'),
    re_path(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/search/description/$',
        views.search_description, name='document-search-description',
    ),
    re_path(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/search/suggestions/$',
        views.search_suggestions, name='document-search-suggestions',
    ),
    re_path(
        r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/(?P<url>[\w./-]*)/$',
        views.document, name='document-detail',
    ),
    re_path(r'^pots/(?P<pot_name>\w+\.pot)$', views.pot_file),
]
