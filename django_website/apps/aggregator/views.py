from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list
from apps.aggregator.models import FeedItem, Feed, FeedType
from apps.aggregator.forms import FeedModelForm

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
    initial_data = {'feed_type': ft.id}
    f = FeedModelForm(request.POST or None, initial=initial_data)
    if f.is_valid():
        if f.save():
            return HttpResponseRedirect(reverse('community-index'))
    return render_to_response('aggregator/add_feed.html',
                              {'form':f},
                              context_instance=RequestContext(request))
