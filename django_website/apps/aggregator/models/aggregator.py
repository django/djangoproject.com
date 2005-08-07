from django.core import meta

class Feed(meta.Model):
    fields = (
        meta.CharField('title', maxlength=200),
        meta.URLField('feed_url', unique=True),
        meta.URLField('public_url'),
        meta.BooleanField("is_defunct"),
    )
    admin = meta.Admin()

    def __repr__(self):
        return self.title

class FeedItem(meta.Model):
    fields = (
        meta.ForeignKey(Feed),
        meta.CharField('title', maxlength=200),
        meta.URLField('link'),
        meta.TextField('summary', blank=True),
        meta.DateTimeField('date_modified'),
        meta.CharField('guid', maxlength=200, unique=True, db_index=True),
    )
    ordering = ("-date_modified",)

    def __repr__(self):
        return self.title
