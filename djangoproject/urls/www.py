from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.contenttypes import views as contenttypes_views
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps import views as sitemap_views
from django.urls import include, path, re_path
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve

from accounts import views as account_views
from aggregator.feeds import (
    CommunityAggregatorFeed, CommunityAggregatorFirehoseFeed,
)
from blog.feeds import WeblogEntryFeed
from blog.sitemaps import WeblogSitemap

admin.autodiscover()

sitemaps = {
    'weblog': WeblogSitemap,
    'flatpages': FlatPageSitemap,
}


urlpatterns = [
    path('', TemplateView.as_view(template_name='homepage.html'), name="homepage"),
    path('start/overview/', TemplateView.as_view(template_name='overview.html'), name="overview"),
    path('start/', TemplateView.as_view(template_name='start.html'), name="start"),
    # to work around a permanent redirect stored in the db that existed before the redesign:
    path('overview/', RedirectView.as_view(url='/start/overview/', permanent=False)),
    path('accounts/', include('accounts.urls')),

    # Admin password reset
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('admin/', admin.site.urls),
    path('community/', include('aggregator.urls')),

    path('conduct/', TemplateView.as_view(template_name='conduct/index.html'), name='code_of_conduct'),
    path('conduct/faq/', TemplateView.as_view(template_name='conduct/faq.html'), name='conduct_faq'),
    path('conduct/reporting/', TemplateView.as_view(template_name='conduct/reporting.html'), name='conduct_reporting'),
    path('conduct/enforcement-manual/', TemplateView.as_view(template_name='conduct/enforcement.html'), name='conduct_enforcement'),
    path('conduct/changes/', TemplateView.as_view(template_name='conduct/changes.html'), name='conduct_changes'),

    path('diversity/', TemplateView.as_view(template_name='diversity/index.html'), name='diversity'),
    path('diversity/changes/', TemplateView.as_view(template_name='diversity/changes.html'), name='diversity_changes'),

    path('contact/', include('contact.urls')),
    path('foundation/minutes/', include('foundation.urls.meetings')),
    path('foundation/', include('members.urls')),
    path('fundraising/', include('fundraising.urls')),

    # Used by docs search suggestions
    re_path(r'^r/(?P<content_type_id>\d+)/(?P<object_id>.*)/$', contenttypes_views.shortcut, name='contenttypes-shortcut'),

    # User stats
    path('~<username>/', account_views.user_profile, name='user_profile'),

    # Feeds
    path('rss/weblog/', WeblogEntryFeed(), name='weblog-feed'),
    path('rss/community/', RedirectView.as_view(url='/rss/community/blogs/')),
    path('rss/community/firehose/', CommunityAggregatorFirehoseFeed(), name='aggregator-firehose-feed'),
    path('rss/community/<slug>/', CommunityAggregatorFeed(), name='aggregator-feed'),

    # django-push
    path('subscriber/', include('django_push.subscriber.urls')),

    # Trac schtuff
    path('trac/', include('tracdb.urls')),

    # Styleguide
    path('styleguide/', TemplateView.as_view(template_name='styleguide.html'), name="styleguide"),

    path('sitemap.xml', cache_page(60 * 60 * 6)(sitemap_views.sitemap), {'sitemaps': sitemaps}),
    path('weblog/', include('blog.urls')),
    path('download/', include('releases.urls')),
    path('svntogit/', include('svntogit.urls')),
    path('', include('legacy.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('m/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
