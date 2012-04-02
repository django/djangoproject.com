from __future__ import absolute_import

import logging
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list
from .models import FeedItem, Feed, FeedType, APPROVED_FEED
from .forms import FeedModelForm
from ..shortcuts import render

def index(request):
    """
    Displays the latest feeds of each type.
    """
    ctx = {'feedtype_list': FeedType.objects.all()}
    return render(request, 'aggregator/index.html', ctx)

def feed_list(request, feed_type_slug):
    """
    Shows the latest feeds for the given type.
    """
    feed_type = get_object_or_404(FeedType, slug=feed_type_slug)
    return object_list(request,
        queryset = FeedItem.objects.filter(feed__feed_type=feed_type, feed__approval_status=APPROVED_FEED),
        paginate_by = 25,
        extra_context = {'feed_type': feed_type},
    )

@login_required
def my_feeds(request):
    """
    Lets the user see, edit, and delete all of their owned feeds.
    """
    feed_types = FeedType.objects.all()
    if not request.user.is_superuser:
        feed_types = feed_types.filter(can_self_add=True)

    ctx = {
        'feeds': Feed.objects.filter(owner=request.user),
        'feed_types': feed_types
    }
    return render(request, 'aggregator/my-feeds.html', ctx)

@login_required
def add_feed(request, feed_type_slug):
    """
    Lets users add new feeds to the aggregator.

    Users only get to add new feeds of types indicated as "can self add."
    """
    ft = get_object_or_404(FeedType, slug=feed_type_slug, can_self_add=True)
    if not ft.can_self_add and not request.user.is_superuser:
        return render(request, 'aggregator/denied.html')

    instance = Feed(feed_type=ft, owner=request.user)
    f = FeedModelForm(request.POST or None, instance=instance)
    if f.is_valid():
        f.save()
        messages.add_message(
            request, messages.INFO, 'Your feed has entered moderation. Please allow up to 1 week for processing.')
        return redirect('community-index')

    ctx = {'form': f, 'feed_type': ft, 'adding': True}
    return render(request, 'aggregator/edit-feed.html', ctx)

@login_required
def edit_feed(request, feed_id):
    """
    Lets a user edit a feed they've previously added.

    Only feeds the user "owns" can be edited.
    """
    feed = get_object_or_404(Feed, pk=feed_id, owner=request.user)
    f = FeedModelForm(request.POST or None, instance=feed)
    if f.is_valid():
        f.save()
        return redirect('community-my-feeds')

    ctx = {'form': f, 'feed': feed, 'adding': False}
    return render(request, 'aggregator/edit-feed.html', ctx)

@login_required
def delete_feed(request, feed_id):
    """
    Lets a user delete a feed they've previously added.

    Only feeds the user "owns" can be deleted.
    """
    feed = get_object_or_404(Feed, pk=feed_id, owner=request.user)
    if request.method == 'POST':
        feed.delete()
        return redirect('community-my-feeds')
    return render(request, 'aggregator/delete-confirm.html', {'feed': feed})
