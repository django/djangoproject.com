from __future__ import absolute_import

from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.comments.feeds import LatestCommentFeed
from django.contrib.comments.models import Comment
from django.contrib.flatpages.views import flatpage
from django.contrib.sitemaps import views as sitemap_views
from django.views.decorators.cache import cache_page
from django.views.generic.simple import redirect_to

from accounts import views as account_views
from aggregator.feeds import CommunityAggregatorFeed, CommunityAggregatorFirehoseFeed
from blog.feeds import WeblogEntryFeed
from django_website.sitemaps import FlatPageSitemap, WeblogSitemap

admin.autodiscover()

comments_info_dict = {
    'queryset': Comment.objects.filter(is_public=True).order_by('-submit_date'),
    'paginate_by': 15,
}

sitemaps = {
    'weblog': WeblogSitemap,
    'flatpages': FlatPageSitemap,
}

handler500 = 'django_website.views.server_error'


urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'homepage.html'}, name="homepage"),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^comments/$', 'django.views.generic.list_detail.object_list', comments_info_dict),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^community/', include('aggregator.urls')),
    url(r'^contact/', include('contact.urls')),
    url(r'^r/', include('django.conf.urls.shortcut')),

    # There's no school like the old school.
    url(r'^~(?P<username>[\w-]+)/$', account_views.user_profile, name='user_profile'),

    # Feeds
    url(r'^rss/weblog/$', WeblogEntryFeed(), name='weblog-feed'),
    url(r'^rss/comments/$', LatestCommentFeed(), name='comments-feed'),
    url(r'^rss/community/$', redirect_to, {'url': '/rss/community/blogs/'}),
    url(r'^rss/community/firehose/$', CommunityAggregatorFirehoseFeed(), name='aggregator-firehose-feed'),
    url(r'^rss/community/(?P<slug>[\w-]+)/$', CommunityAggregatorFeed(), name='aggregator-feed'),

    # PayPal insists on POSTing to the "thank you" page which means we can't
    # just use a flatpage for it.
    url(r'^foundation/donate/thanks/$', 'django_website.views.donate_thanks'),

    # django-push
    url(r'^subscriber/', include('django_push.subscriber.urls')),

    url(r'^sitemap\.xml$', cache_page(sitemap_views.sitemap, 60 * 60 * 6), {'sitemaps': sitemaps}),
    url(r'^weblog/', include('blog.urls')),
    url(r'^download$', flatpage, {'url': 'download'}, name="download"),
    url(r'^svntogit/', include('svntogit.urls')),
    url(r'', include('legacy.urls')),
)
