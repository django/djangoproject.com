from django.db import models

class Feed(models.Model):
    title = models.CharField(maxlength=200)
    feed_url = models.URLField(unique=True)
    public_url = models.URLField()
    is_defunct = models.BooleanField()

    class Meta:
        db_table = 'aggregator_feeds'

    class Admin:
        pass

    def __str__(self):
        return self.title

class FeedItem(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(maxlength=200)
    link = models.URLField()
    summary = models.TextField(blank=True)
    date_modified = models.DateTimeField()
    guid = models.CharField(maxlength=200, unique=True, db_index=True)

    class Meta:
        db_table = 'aggregator_feeditems'
        ordering = ("-date_modified",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return self.link
