from django.db import models

class Document(models.Model):
    title = models.CharField(maxlength=200)
    slug = models.CharField(maxlength=50, unique=True, prepopulate_from=('title',))
    doc_path = models.CharField(maxlength=200,
        help_text="Relative to the docs directory in django SVN. Leave off the file extension.")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'docs_documents'
        ordering = ('title',)

    class Admin:
        fields = (
            (None, {'fields': ('title', 'slug', 'doc_path')}),
        )
        list_display = ('title', 'doc_path')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return "/documentation/%s/" % self.slug

    def get_content(self):
        try:
            return self._doc_content
        except AttributeError:
            import os
            from django.conf import settings
            doc_path = os.path.join(settings.DJANGO_DOCUMENT_ROOT_PATH, "%s.html" % self.doc_path)
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
            from django.conf import settings
            toc_path = os.path.join(settings.DJANGO_DOCUMENT_ROOT_PATH, "%s_toc.html" % self.doc_path)
            if os.path.exists(toc_path):
                self._toc_content = open(toc_path).read()
            else:
                self._toc_content = ''
            return self._toc_content
