from django.conf.urls import url
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    url(r'^$', views.index, name='homepage'),
    url(r'^search/$', views.redirect_search),
    url(r'^(?P<lang>[a-z-]+)/$', views.language),
    url(
        r'^[a-z-]+/[\w.-]+/internals/team/$',
        RedirectView.as_view(
            url='https://www.djangoproject.com/foundation/teams/',
            permanent=True,
        )
    ),
    url(r'^(?P<lang>[a-z-]+)/(?P<version>stable)/(?P<url>.*)$', views.stable),
    url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/$', views.document,
        {'url': ''}, name='document-index'),
    url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_objects/$',
        views.objects_inventory, name='objects-inv'),
    url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_images/(?P<path>.*)$',
        views.sphinx_static, {'subpath': '_images'}, name='sphinx-images'),
    url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_source/(?P<path>.*)$',
        views.sphinx_static, {'subpath': '_sources'}, name='sphinx-sources'),
    url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/_downloads/(?P<path>.*)$',
        views.sphinx_static, {'subpath': '_downloads'}, name='sphinx-downloads'),
    url(r'^(.*)/index/$', views.redirect_index),
    url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/search/$',
        views.search_results, name='document-search'),
    url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/search/description/$',
        views.search_description, name='document-search-description'),
    url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/search/suggestions/$',
        views.search_suggestions, name='document-search-suggestions'),
    url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/(?P<url>[\w./-]*)/$',
        views.document, name='document-detail'),
    url(r'^pots/(?P<pot_name>\w+\.pot)$', views.pot_file),
]
