from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.list import ListView

from .forms import FeedModelForm
from .models import APPROVED_FEED, Feed, FeedItem, FeedType


def index(request):
    """
    Displays the latest feeds of each type.
    """
    feeds = []
    for ft in FeedType.objects.all():
        feeds.append((ft, ft.items()[0:5]))
    ctx = {'feedtype_list': feeds}
    return render(request, 'aggregator/index.html', ctx)


class FeedListView(ListView):
    """
    Shows the latest feeds for the given type.
    """

    paginate_by = 25

    def get_queryset(self):
        self.feed_type = get_object_or_404(FeedType, slug=self.kwargs.pop('feed_type_slug'))
        return FeedItem.objects.filter(feed__feed_type=self.feed_type, feed__approval_status=APPROVED_FEED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed_type'] = self.feed_type
        return context


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
