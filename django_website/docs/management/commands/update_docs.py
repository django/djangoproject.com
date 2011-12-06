"""
Update and build the documentation into files for display with the djangodocs
app.
"""
from __future__ import absolute_import

import json
import haystack
import optparse
import subprocess
import zipfile
import sphinx.cmdline
from contextlib import closing
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.utils.html import strip_tags
from unipath import FSPath as Path
from ...models import DocumentRelease, Document

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        optparse.make_option(
            '--skip-indexing',
            action='store_false',
            dest='reindex',
            default=True,
            help='Skip reindexing (for testing, mostly).'
        ),
    )

    def handle_noargs(self, **kwargs):
        try:
            verbosity = int(kwargs['verbosity'])
        except (KeyError, TypeError, ValueError):
            verbosity = 1

        for release in DocumentRelease.objects.all():
            if verbosity >= 1:
                print "Updating %s..." % release

            destdir = Path(settings.DOCS_BUILD_ROOT).child(release.lang, release.version)
            if not destdir.exists():
                destdir.mkdir(parents=True)

            #
            # Update the release from SCM.
            #

            # Make an SCM checkout/update into the destination directory.
            # Do this dynamically in case we add other SCM later.
            getattr(self, 'update_%s' % release.scm)(release.scm_url, destdir)

            #
            # Use Sphinx to build the release docs into JSON and HTML documents.
            #
            for builder in ('json', 'html'):
                # Make the directory for the built files - sphinx-build doesn't
                # do it for us, apparently.
                build_dir = destdir.child('_build', builder)
                if not build_dir.exists():
                    build_dir.mkdir(parents=True)

                # "Shell out" (not exactly, but basically) to sphinx-build.
                if verbosity >= 2:
                    print "  building %s (into %s)" % (builder, build_dir)
                sphinx.cmdline.main(['sphinx-build',
                    '-b', builder,
                    '-q',              # Be vewy qwiet
                    destdir,           # Source file directory
                    build_dir,         # Destination directory
                ])

            #
            # Create a zip file of the HTML build for offline reading.
            # This gets moved into MEDIA_ROOT for downloading.
            #
            html_build_dir = destdir.child('_build', 'html')
            zipfile_name = 'django-docs-%s-%s.zip' % (release.version, release.lang)
            zipfile_path = Path(settings.MEDIA_ROOT).child('docs', zipfile_name)
            if not zipfile_path.parent.exists():
                zipfile_path.parent.mkdir(parents=True)
            if verbosity >= 2:
                print "  build zip (into %s)" % zipfile_path
            with closing(zipfile.ZipFile(zipfile_path, 'w')) as zf:
                for f in html_build_dir.walk(filter=Path.isfile):
                    zf.write(f, html_build_dir.rel_path_to(f))

            #
            # Rebuild the imported document list and search index.
            #
            if not kwargs['reindex']:
                continue

            if verbosity >= 2:
                print "  reindexing..."

            # Build a dict of {path_fragment: document_object}. We'll pop values
            # out of this dict as we go which'll make sure we know which
            # remaining documents need to be deleted (and unindexed) later on.
            documents = dict((doc.path, doc) for doc in release.documents.all())

            # Walk the tree we've just built looking for ".fjson" documents
            # (just JSON, but Sphinx names them weirdly). Each one of those
            # documents gets a corresponding Document object created which
            # we'll then ask Sphinx to reindex.
            #
            # We have to be a bit careful to reverse-engineer the correct
            # relative path component, especially for "index" documents,
            # otherwise the search results will be incorrect.
            json_build_dir = destdir.child('_build', 'json')
            for built_doc in json_build_dir.walk():
                if built_doc.isfile() and built_doc.ext == '.fjson':

                    # Convert the built_doc path which is now an absolute
                    # path (i.e. "/home/docs/en/1.2/_build/ref/models.json")
                    # into a path component (i.e. "ref/models").
                    path = json_build_dir.rel_path_to(built_doc)
                    if path.stem == 'index':
                        path = path.parent
                    path = str(path.parent.child(path.stem))

                    # Read out the content and create a new Document object for
                    # it. We'll strip the HTML tags here (for want of a better
                    # place to do it).
                    with open(built_doc) as fp:
                        json_doc = json.load(fp)
                        try:
                            json_doc['body']  # Just to make sure it exists.
                            title = strip_tags(json_doc['title'])
                        except KeyError, ex:
                            if verbosity >= 2:
                                print "Skipping: %s (no %s)" % (path, ex.args[0])
                            continue

                    doc = documents.pop(path, Document(path=path, release=release))
                    doc.title = title
                    doc.save()
                    haystack.site.update_object(doc)

            # Clean up any remaining documents.
            for doc in documents.values():
                if verbosity >= 2:
                    print "Deleting:", doc
                haystack.site.remove_object(doc)
                doc.delete()

    def update_svn(self, url, destdir):
        subprocess.call(['svn', 'checkout', '-q', url, destdir])
