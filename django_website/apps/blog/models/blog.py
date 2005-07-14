from django.core import meta

class Entry(meta.Model):
    verbose_name_plural = 'entries'
    module_name = 'entries'
    fields = (
        meta.DateTimeField('pub_date', 'publication date'),
        meta.SlugField('slug', 'slug', unique_for_date='pub_date'),
        meta.CharField('headline', 'headline', maxlength=200),
        meta.TextField('body', 'body', help_text="Use raw HTML."),
    )
    ordering = (('pub_date', 'DESC'),)
    admin = meta.Admin(
        fields = (
            (None, {'fields': ('pub_date', 'slug', 'headline', 'body')}),
        ),
        list_display = ('pub_date', 'headline'),
    )

    def __repr__(self):
        return self.headline

    def get_absolute_url(self):
        return "/weblog/%s/%s/" % (self.pub_date.strftime("%Y/%b/%d").lower(), self.slug)
