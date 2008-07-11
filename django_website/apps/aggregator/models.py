from django.db import models

class Feed(models.Model):
    title = models.CharField(maxlength=500)
    feed_url = models.URLField(unique=True, maxlength=500)
    public_url = models.URLField(maxlength=500)
    is_defunct = models.BooleanField()

    class Meta:
        db_table = 'aggregator_feeds'

    class Admin:
        list_display = ["title", "public_url", "is_defunct"]
        list_filter = ["is_defunct"]
        ordering = ["title"]
        search_fields = ["title", "public_url"]
        list_per_page = 500

    def __unicode__(self):
        return self.title

class FeedItem(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(maxlength=500)
    link = models.URLField(maxlength=500)
    summary = models.TextField(blank=True)
    date_modified = models.DateTimeField()
    guid = models.CharField(maxlength=500, unique=True, db_index=True)

    class Meta:
        db_table = 'aggregator_feeditems'
        ordering = ("-date_modified",)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.link
