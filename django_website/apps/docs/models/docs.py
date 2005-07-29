from django.core import meta

class Document(meta.Model):
    fields = (
        meta.CharField('title', maxlength=200),
        meta.CharField('slug', maxlength=50, unique=True, prepopulate_from=('title',)),
        meta.CharField('doc_path', maxlength=200,
            help_text="Relative to the docs directory in django SVN; leave off the file extension"),
        meta.DateTimeField('last_updated', 'last updated', auto_now=True),
    )
    ordering = ('title',)
    admin = meta.Admin(
        fields = (
            (None, {'fields': ('title', 'slug', 'doc_path')}),
        ),
        list_display = ('title', 'doc_path'),
    )

    def __repr__(self):
        return self.title

    def get_absolute_url(self):
        return "/documentation/%s/" % self.slug

    def get_content(self):
        try:
            return self._doc_content
        except AttributeError:
            import os
            from django.conf.settings import DJANGO_DOCUMENT_ROOT_PATH
            doc_path = os.path.join(DJANGO_DOCUMENT_ROOT_PATH, "%s.html" % self.doc_path)
            if os.path.exists(doc_path):
                self._doc_content = open(doc_path).read()
            else:
                self._doc_content = ''
            return self._doc_content

    def get_toc(self):
        try:
            return self._toc_content
        except AttributeError:
            import os
            from django.conf.settings import DJANGO_DOCUMENT_ROOT_PATH
            toc_path = os.path.join(DJANGO_DOCUMENT_ROOT_PATH, "%s_toc.html" % self.doc_path)
            if os.path.exists(toc_path):
                self._toc_content = open(toc_path).read()
            else:
                self._toc_content = ''
            return self._toc_content
