from django_push.publisher.feeds import Feed


class HubFeed(Feed):
    link = '/feed/'

    def items(self):
        return [1, 2, 3]

    def item_title(self, item):
        return str(item)

    def item_link(self, item):
        return '/items/{0}'.format(item)


class OverrideHubFeed(HubFeed):
    link = '/overriden-feed/'
    hub = 'http://example.com/overridden-hub'


class DynamicHubFeed(HubFeed):
    link = '/dynamic-feed/'

    def get_hub(self, obj):
        return 'http://dynamic-hub.example.com/'
