from django.db import models

class FeedType(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    can_self_add = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % (self.name,)

    def items(self):
        return FeedItem.objects.filter(feed__feed_type=self)

class Feed(models.Model):
    title = models.CharField(max_length=500)
    feed_url = models.URLField(unique=True, max_length=500)
    public_url = models.URLField(max_length=500)
    is_defunct = models.BooleanField()
    feed_type = models.ForeignKey(FeedType)

    class Meta:
        db_table = 'aggregator_feeds'

    def __unicode__(self):
        return self.title

class FeedItemManager(models.Manager):
    def create_or_update_by_guid(self, guid, **kwargs):
        """
        Look up a FeedItem by GUID, updating it if it exists, and creating
        it if it doesn't.
        
        We don't limit it by feed because an item could be in another feed if
        some feeds are themselves aggregators. That's also why we don't update
        the feed field if the feed item already exists.
        
        Returns (item, created) like get_or_create().
        """
        try:
            item = self.get(guid=guid)
        
        except self.model.DoesNotExist:
            # Create a new item
            kwargs['guid'] = guid
            item = self.create(**kwargs)
            
        else:
            # Update an existing one.
            kwargs.pop('feed', None)
            for k,v in kwargs.items():
                setattr(item, k, v)
            item.save()
            
        return item
        
class FeedItem(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=500)
    link = models.URLField(max_length=500)
    summary = models.TextField(blank=True)
    date_modified = models.DateTimeField()
    guid = models.CharField(max_length=500, unique=True, db_index=True)

    objects = FeedItemManager()

    class Meta:
        db_table = 'aggregator_feeditems'
        ordering = ("-date_modified",)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.link
