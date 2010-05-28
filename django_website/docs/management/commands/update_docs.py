"""
Update and build the documentation into files for display with the djangodocs
app.
"""
from __future__ import absolute_import

import subprocess
from django.conf import settings
from django.core.management.base import NoArgsCommand
from unipath import FSPath as Path
from ...models import DocumentRelease

class Command(NoArgsCommand):
    def handle_noargs(self, **kwargs):
        for release in DocumentRelease.objects.all():
            print "Updating %s..." % release
            destdir = Path(settings.DOCS_BUILD_ROOT).child(release.lang, release.version)
            if not destdir.exists():
                destdir.mkdir(parents=True)
            
            # Make an SCM checkout/update into the destination directory.
            # Do this dynamically in case we add other SCM later.
            getattr(self, 'update_%s' % release.scm)(release.scm_url, destdir)

            # Run Sphinx by faking a commandline. Better than shelling out, I s'pose.
            subprocess.call(['sphinx-build',
                '-b', 'json',                       # Use the JSON builder
                '-q',                               # Be vewy qwiet
                destdir,                            # Source file directory
                destdir.child('_build', 'json'),    # Destination directory
            ])

    def update_svn(self, url, destdir):
        subprocess.call(['svn', 'checkout', url, destdir])