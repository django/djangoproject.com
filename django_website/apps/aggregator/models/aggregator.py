from django.core import meta

class Feed(meta.Model):
    title = meta.CharField(maxlength=200)
    feed_url = meta.URLField(unique=True)
    public_url = meta.URLField()
    is_defunct = meta.BooleanField()
    class META:
        admin = meta.Admin()

    def __repr__(self):
        return self.title

class FeedItem(meta.Model):
    feed = meta.ForeignKey(Feed)
    title = meta.CharField(maxlength=200)
    link = meta.URLField()
    summary = meta.TextField(blank=True)
    date_modified = meta.DateTimeField()
    guid = meta.CharField(maxlength=200, unique=True, db_index=True)
    class META:
        ordering = ("-date_modified",)

    def __repr__(self):
        return self.title

    def get_absolute_url(self):
        return self.link
