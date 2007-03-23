from django.conf.urls.defaults import *
from django.contrib.comments.feeds import LatestFreeCommentsFeed
from django.contrib.comments.models import FreeComment
from django.contrib.sitemaps import views as sitemap_views
from django_website.apps.aggregator.feeds import CommunityAggregatorFeed
from django_website.apps.aggregator.models import FeedItem
from django_website.apps.blog.feeds import WeblogEntryFeed
from django_website.sitemaps import FlatPageSitemap, WeblogSitemap
from django.views.decorators.cache import cache_page

comments_info_dict = {
    'queryset': FreeComment.objects.all(),
    'paginate_by': 15,
}

aggregator_info_dict = {
    'queryset': FeedItem.objects.select_related(),
    'paginate_by': 15,
}

feeds = {
    'weblog': WeblogEntryFeed,
    'comments': LatestFreeCommentsFeed,
    'community': CommunityAggregatorFeed,
}

sitemaps = {
    'weblog': WeblogSitemap,
    'flatpages': FlatPageSitemap,
}

urlpatterns = patterns('',
    (r'^weblog/', include('django_website.apps.blog.urls')),
    (r'^documentation/', include('django_website.apps.docs.urls')),
    (r'^comments/$', 'django.views.generic.list_detail.object_list', comments_info_dict),
    (r'^comments/', include('django.contrib.comments.urls.comments')),
    (r'^community/$', 'django.views.generic.list_detail.object_list', aggregator_info_dict),
    (r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^password_reset/', include('django.conf.urls.admin_password_reset')),
    (r'^r/', include('django.conf.urls.shortcut')),
    (r'^sitemap.xml$', cache_page(sitemap_views.sitemap, 60 * 60 * 6), {'sitemaps': sitemaps}),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'', include('django.contrib.flatpages.urls')),
)
