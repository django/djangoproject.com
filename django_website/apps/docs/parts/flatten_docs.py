"""
Utility that converts all current Django documents to flat pages.

We use this to flatten/freeze the current Django documentation for
a particular version.
"""

from django.models.flatpages import flatpages
from django.models.docs import documents

for doc in documents.get_list():
    f = flatpages.FlatPage(
        url='/documentation/0_91/%s/' % doc.slug,
        title='Documentation (version 0.91) | %s' % doc.title,
        content='%s</div><div id="content-related" class="sidebar"><h2>Contents</h2>%s' % (doc.get_content(), doc.get_toc()),
        enable_comments=False,
        template_name='flatfiles/legacy_docs',
        registration_required=False)
    f.save()
    f.set_sites([1])
