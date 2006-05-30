"""
Utility that converts all current Django documents to flat pages.

We use this to flatten/freeze the current Django documentation for
a particular version.
"""

from django_website.apps.docs.models import Document
from django.contrib.flatpages.models import FlatPage

for doc in Document.objects.all():
    f = FlatPage(
        url='/documentation/0_91/%s/' % doc.slug,
        title='Documentation (version 0.91) | %s' % doc.title,
        content='%s</div><div id="content-related" class="sidebar"><h2>Contents</h2>%s' % (doc.get_content(), doc.get_toc()),
        enable_comments=False,
        template_name='flatfiles/legacy_docs',
        registration_required=False)
    f.save()
    f.site_set = [1]
