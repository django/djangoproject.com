from django.core import meta

class Entry(meta.Model):
    pub_date = meta.DateTimeField()
    slug = meta.SlugField(unique_for_date='pub_date')
    headline = meta.CharField(maxlength=200)
    summary = meta.TextField(help_text="Use raw HTML.")
    body = meta.TextField(help_text="Use raw HTML.")
    author = meta.CharField(maxlength=100)
    class META:
        verbose_name_plural = 'entries'
        module_name = 'entries'
        ordering = ('-pub_date',)
        get_latest_by = 'pub_date'
        admin = meta.Admin(
            list_display = ('pub_date', 'headline', 'author'),
        )

    def __repr__(self):
        return self.headline

    def get_absolute_url(self):
        return "/weblog/%s/%s/" % (self.pub_date.strftime("%Y/%b/%d").lower(), self.slug)
