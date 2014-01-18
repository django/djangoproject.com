from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.flatpages.views import flatpage
from django.contrib.sitemaps import FlatPageSitemap
from django.contrib.sitemaps import views as sitemap_views
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from django.views.generic import RedirectView, TemplateView

from accounts import views as account_views
from aggregator.feeds import CommunityAggregatorFeed, CommunityAggregatorFirehoseFeed
from blog.feeds import WeblogEntryFeed
from blog.sitemaps import WeblogSitemap

admin.autodiscover()

sitemaps = {
    'weblog': WeblogSitemap,
    'flatpages': FlatPageSitemap,
}

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='homepage.html'), name="homepage"),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^community/', include('aggregator.urls')),
    url(r'^conduct/$', TemplateView.as_view(template_name='conduct/index.html'), name='code_of_conduct'),
    url(r'^conduct/faq/$', TemplateView.as_view(template_name='conduct/faq.html'), name='conduct_faq'),
    url(r'^conduct/reporting/$', TemplateView.as_view(template_name='conduct/reporting.html'), name='conduct_reporting'),
    url(r'^conduct/enforcement-manual/$', TemplateView.as_view(template_name='conduct/enforcement.html'), name='conduct_enforcement'),
    url(r'^conduct/changes/$', TemplateView.as_view(template_name='conduct/changes.html'), name='conduct_enforcement'),
    url(r'^contact/', include('contact.urls')),
    url(r'^r/(?P<content_type_id>\d+)/(?P<object_id>.*)/$', 'django.contrib.contenttypes.views.shortcut'),

    # There's no school like the old school.
    url(r'^~(?P<username>[\w-]+)/$', account_views.user_profile, name='user_profile'),

    # Feeds
    url(r'^rss/weblog/$', WeblogEntryFeed(), name='weblog-feed'),
    url(r'^rss/community/$', RedirectView.as_view(url='/rss/community/blogs/')),
    url(r'^rss/community/firehose/$', CommunityAggregatorFirehoseFeed(), name='aggregator-firehose-feed'),
    url(r'^rss/community/(?P<slug>[\w-]+)/$', CommunityAggregatorFeed(), name='aggregator-feed'),

    # PayPal insists on POSTing to the "thank you" page which means we can't
    # just use a flatpage for it.
    url(r'^foundation/donate/thanks/$', csrf_exempt(lambda req: render(req, 'donate_thanks.html'))),

    # django-push
    url(r'^subscriber/', include('django_push.subscriber.urls')),

    # Trac schtuff
    url(r'^trac/', include('tracdb.urls')),


    url(r'^sitemap\.xml$', cache_page(60 * 60 * 6)(sitemap_views.sitemap), {'sitemaps': sitemaps}),
    url(r'^weblog/', include('blog.urls')),
    url(r'^download/', include('releases.urls')),
    url(r'^svntogit/', include('svntogit.urls')),
    url(r'', include('legacy.urls')),
)

@requires_csrf_token
def handler500(request):
    return render(request, '500.html')
