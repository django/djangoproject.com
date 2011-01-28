"""
Update and build the documentation into files for display with the djangodocs
app.
"""
from __future__ import absolute_import

import subprocess
import sphinx.cmdline
from django.conf import settings
from django.core.management.base import NoArgsCommand
from unipath import FSPath as Path
from ...models import DocumentRelease

class Command(NoArgsCommand):
    def handle_noargs(self, **kwargs):
        try:
            verbose = int(kwargs['verbosity']) > 0
        except (KeyError, TypeError, ValueError):
            verbose = True
        
        for release in DocumentRelease.objects.all():
            if verbose:
                print "Updating %s..." % release
                
            destdir = Path(settings.DOCS_BUILD_ROOT).child(release.lang, release.version)
            if not destdir.exists():
                destdir.mkdir(parents=True)
            
            # Make an SCM checkout/update into the destination directory.
            # Do this dynamically in case we add other SCM later.
            getattr(self, 'update_%s' % release.scm)(release.scm_url, destdir)
            
            # Make the directory for the JSON files - sphinx-build doesn't
            # do it for us, apparently.
            json_build_dir = destdir.child('_build', 'json')
            if not json_build_dir.exists():
                json_build_dir.mkdir(parents=True)
            
            # "Shell out" (not exactly, but basically) to sphinx-build.
            sphinx.cmdline.main(['sphinx-build',
                '-b', 'json',      # Use the JSON builder
                '-q',              # Be vewy qwiet
                destdir,           # Source file directory
                json_build_dir,    # Destination directory
            ])

    def update_svn(self, url, destdir):
        subprocess.call(['svn', 'checkout', '-q', url, destdir])