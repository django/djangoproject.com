from __future__ import absolute_import

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list
from .models import FeedItem, Feed, FeedType
from .forms import FeedModelForm

def index(request):
    feedtype_list = FeedType.objects.all()
    return render_to_response('aggregator/index.html',
                              {'feedtype_list': feedtype_list},
                              context_instance=RequestContext(request))

def feed_list(request, feed_type_slug):
    feed_type = get_object_or_404(FeedType, slug=feed_type_slug)
    items = FeedItem.objects.filter(feed__feed_type=feed_type)
    return object_list(request, items)

@login_required
def add_feed(request, feed_type_slug):
    ft = get_object_or_404(FeedType, slug=feed_type_slug, can_self_add=True)
    if not ft.can_self_add and not request.user.is_superuser:
        return render_to_response('aggregator/denied.html',
                                  context_instance=RequestContext(request))
        
    instance = Feed(feed_type=ft)
    f = FeedModelForm(request.POST or None, instance=instance)
    if f.is_valid():
        if f.save():
            return HttpResponseRedirect(reverse('community-index'))
    return render_to_response('aggregator/add_feed.html',
                              {'form':f, 'feed_type': ft},
                              context_instance=RequestContext(request))
