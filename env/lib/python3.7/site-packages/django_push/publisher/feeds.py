from django.conf import settings
from django.contrib.syndication.views import Feed as BaseFeed
from django.utils.feedgenerator import Atom1Feed


class HubAtom1Feed(Atom1Feed):
    def add_root_elements(self, handler):
        super(HubAtom1Feed, self).add_root_elements(handler)

        hub = self.feed.get('hub')
        if hub is not None:
            handler.addQuickElement('link', '', {'rel': 'hub',
                                                 'href': hub})


class Feed(BaseFeed):
    feed_type = HubAtom1Feed
    hub = None

    def get_hub(self, obj):
        if self.hub is None:
            hub = getattr(settings, 'PUSH_HUB', None)
        else:
            hub = self.hub
        return hub

    def feed_extra_kwargs(self, obj):
        kwargs = super(Feed, self).feed_extra_kwargs(obj)
        kwargs['hub'] = self.get_hub(obj)
        return kwargs
