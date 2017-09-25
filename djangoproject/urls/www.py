from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views as auth_views
from django.contrib.contenttypes import views as contenttypes_views
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps import views as sitemap_views
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve
from markdownx.views import MarkdownifyView

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
    url(r'^$', TemplateView.as_view(template_name='homepage.html'), name="homepage"),
    url(r'^start/overview/$', TemplateView.as_view(template_name='overview.html'), name="overview"),
    url(r'^start/$', TemplateView.as_view(template_name='start.html'), name="start"),
    # to work around a permanent redirect stored in the db that existed before the redesign:
    url(r'^overview/$', RedirectView.as_view(url='/start/overview/', permanent=False)),
    url(r'^accounts/', include('accounts.urls')),

    # Admin password reset
    url(r'^admin/password_reset/$', auth_views.PasswordResetView.as_view(), name='admin_password_reset'),
    url(r'^admin/password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    url(r'^admin/', admin.site.urls),
    url(r'^community/', include('aggregator.urls')),

    url(r'^conduct/$', TemplateView.as_view(template_name='conduct/index.html'), name='code_of_conduct'),
    url(r'^conduct/faq/$', TemplateView.as_view(template_name='conduct/faq.html'), name='conduct_faq'),
    url(r'^conduct/reporting/$', TemplateView.as_view(template_name='conduct/reporting.html'), name='conduct_reporting'),
    url(r'^conduct/enforcement-manual/$', TemplateView.as_view(template_name='conduct/enforcement.html'), name='conduct_enforcement'),
    url(r'^conduct/changes/$', TemplateView.as_view(template_name='conduct/changes.html'), name='conduct_changes'),

    url(r'^diversity/$', TemplateView.as_view(template_name='diversity/index.html'), name='diversity'),
    url(r'^diversity/changes/$', TemplateView.as_view(template_name='diversity/changes.html'), name='diversity_changes'),

    url(r'^contact/', include('contact.urls')),
    url(r'^foundation/', include('members.urls')),
    url(r'^fundraising/', include('fundraising.urls')),
    url(r'^markdownx/markdownify/$', staff_member_required(MarkdownifyView.as_view())),

    # Used by docs search suggestions
    url(r'^r/(?P<content_type_id>\d+)/(?P<object_id>.*)/$', contenttypes_views.shortcut, name='contenttypes-shortcut'),

    # User stats
    url(r'^~(?P<username>[\w.@+-]+)/$', account_views.user_profile, name='user_profile'),

    # Feeds
    url(r'^rss/weblog/$', WeblogEntryFeed(), name='weblog-feed'),
    url(r'^rss/community/$', RedirectView.as_view(url='/rss/community/blogs/')),
    url(r'^rss/community/firehose/$', CommunityAggregatorFirehoseFeed(), name='aggregator-firehose-feed'),
    url(r'^rss/community/(?P<slug>[\w-]+)/$', CommunityAggregatorFeed(), name='aggregator-feed'),

    # django-push
    url(r'^subscriber/', include('django_push.subscriber.urls')),

    # Trac schtuff
    url(r'^trac/', include('tracdb.urls')),

    # Styleguide
    url(r'^styleguide/$', TemplateView.as_view(template_name='styleguide.html'), name="styleguide"),

    url(r'^sitemap\.xml$', cache_page(60 * 60 * 6)(sitemap_views.sitemap), {'sitemaps': sitemaps}),
    url(r'^weblog/', include('blog.urls')),
    url(r'^download/', include('releases.urls')),
    url(r'^svntogit/', include('svntogit.urls')),
    url(r'', include('legacy.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^m/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
