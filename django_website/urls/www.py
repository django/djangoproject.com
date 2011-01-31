from __future__ import absolute_import

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.comments.feeds import LatestCommentFeed
from django.contrib.comments.models import Comment
from django.contrib.sitemaps import views as sitemap_views
from django.views.decorators.cache import cache_page
from django.views.generic.simple import redirect_to
from ..aggregator.feeds import CommunityAggregatorFeed, CommunityAggregatorFirehoseFeed
from ..aggregator.models import FeedItem
from ..blog.feeds import WeblogEntryFeed
from ..sitemaps import FlatPageSitemap, WeblogSitemap

comments_info_dict = {
    'queryset': Comment.objects.filter(is_public=True).order_by('-submit_date'),
    'paginate_by': 15,
}

sitemaps = {
    'weblog': WeblogSitemap,
    'flatpages': FlatPageSitemap,
}

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'homepage.html'}, name="homepage"),
    url(r'^accounts/', include('django_website.accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^comments/$', 'django.views.generic.list_detail.object_list', comments_info_dict),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^community/', include('django_website.aggregator.urls')),
    url(r'^contact/', include('django_website.contact.urls')),
    url(r'^r/', include('django.conf.urls.shortcut')),

    url(r'^rss/weblog/$', WeblogEntryFeed(), name='weblog-feed'),
    url(r'^rss/comments/$', LatestCommentFeed(), name='comments-feed'),
    url(r'^rss/community/$', redirect_to, {'url': '/rss/community/blogs/'}),
    url(r'^rss/community/firehose/$', CommunityAggregatorFirehoseFeed(), name='aggregator-firehose-feed'),
    url(r'^rss/community/(?P<slug>[\w-]+)/$', CommunityAggregatorFeed(), name='aggregator-feed'),

    url(r'^sitemap\.xml$', cache_page(sitemap_views.sitemap, 60 * 60 * 6), {'sitemaps': sitemaps}),
    url(r'^weblog/', include('django_website.blog.urls')),
    url(r'^freenode\.9xJY7YIUWtwn\.html$', 'django.views.generic.simple.direct_to_template', {'template': 'freenode_tmp.html'}),
    url(r'^download$', 'django.contrib.flatpages.views.flatpage', {'url': 'download'}, name="download"),
    url(r'', include('django_website.legacy.urls')),
)

if not settings.PRODUCTION:
    urlpatterns += patterns("django.views",
        url(r"^media/(?P<path>.*)", "static.serve", {
            "document_root": settings.MEDIA_ROOT,
        }),
    )

urlpatterns += patterns('',
    # flatpages need to be last b/c they match anything
    (r'', include('django.contrib.flatpages.urls')),
)

admin.autodiscover()
