"""
Update and build the documentation into files for display with the djangodocs
app.
"""
from __future__ import absolute_import

import os
import json
import haystack
import optparse
import shutil
import subprocess
import zipfile
import sphinx.cmdline
from contextlib import closing
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.utils.html import strip_tags
from django.utils.text import unescape_entities
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

        # Somehow, bizarely, there's a bug in Sphinx such that if I try to
        # build 1.0 before other versions, things fail in weird ways. However,
        # building newer versions first works. I suspect Sphinx is hanging onto
        # some global state. Anyway, we can work around it by making sure that
        # "dev" builds before "1.0". This is ugly, but oh well.
        for release in DocumentRelease.objects.order_by('-version'):
            if verbosity >= 1:
                print "Updating %s..." % release

            # checkout_dir is shared for all languages.
            checkout_dir = Path(settings.DOCS_BUILD_ROOT).child(release.version)
            parent_build_dir = Path(settings.DOCS_BUILD_ROOT).child(release.lang, release.version)
            if not checkout_dir.exists():
                checkout_dir.mkdir(parents=True)
            if not parent_build_dir.exists():
                parent_build_dir.mkdir(parents=True)

            #
            # Update the release from SCM.
            #

            # Make an SCM checkout/update into the destination directory.
            # Do this dynamically in case we add other SCM later.
            getattr(self, 'update_%s' % release.scm)(release.scm_url, checkout_dir)

            if release.docs_subdir:
                source_dir = checkout_dir.child(*release.docs_subdir.split('/'))
            else:
                source_dir = checkout_dir

            if release.lang != 'en':
                scm_url = release.scm_url.replace('django.git', 'django-docs-translations.git')
                trans_dir = checkout_dir.child('django-docs-translation')
                if not trans_dir.exists():
                    trans_dir.mkdir()
                getattr(self, 'update_%s' % release.scm)(scm_url, trans_dir)
                if not source_dir.child('locale').exists():
                    source_dir.child('locale').write_link(trans_dir.child('translations'))
                subprocess.call("cd %s && make translations" % trans_dir, shell=True)

            #
            # Use Sphinx to build the release docs into JSON and HTML documents.
            #
            for builder in ('json', 'html'):
                # Wipe and re-create the build directory. See #18930.
                build_dir = parent_build_dir.child('_build', builder)
                if build_dir.exists():
                    shutil.rmtree(build_dir)
                build_dir.mkdir(parents=True)

                # "Shell out" (not exactly, but basically) to sphinx-build.
                if verbosity >= 2:
                    print "  building %s (%s -> %s)" % (builder, source_dir, build_dir)
                sphinx.cmdline.main(['sphinx-build',
                    '-b', builder,
                    '-D', 'language=%s' % release.lang,
                    '-q',              # Be vewy qwiet
                    source_dir,        # Source file directory
                    build_dir,         # Destination directory
                ])

            #
            # Create a zip file of the HTML build for offline reading.
            # This gets moved into STATIC_ROOT for downloading.
            #
            html_build_dir = parent_build_dir.child('_build', 'html')
            zipfile_name = 'django-docs-%s-%s.zip' % (release.version, release.lang)
            zipfile_path = Path(settings.STATIC_ROOT).child('docs', zipfile_name)
            if not zipfile_path.parent.exists():
                zipfile_path.parent.mkdir(parents=True)
            if verbosity >= 2:
                print "  build zip (into %s)" % zipfile_path

            def zipfile_inclusion_filter(f):
                return f.isfile() and '.doctrees' not in f.components()

            with closing(zipfile.ZipFile(zipfile_path, 'w')) as zf:
                for f in html_build_dir.walk(filter=zipfile_inclusion_filter):
                    zf.write(f, html_build_dir.rel_path_to(f))

            #
            # Copy the build results to the directory used for serving
            # the documentation in the least disruptive way possible.
            #
            build_dir = parent_build_dir.child('_build')
            built_dir = parent_build_dir.child('_built')
            subprocess.check_call(['rsync', '--archive', '--delete',
                    '--link-dest=' + build_dir, build_dir + '/', built_dir])

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
            json_built_dir = parent_build_dir.child('_built', 'json')
            for built_doc in json_built_dir.walk():
                if built_doc.isfile() and built_doc.ext == '.fjson':

                    # Convert the built_doc path which is now an absolute
                    # path (i.e. "/home/docs/en/1.2/_built/ref/models.json")
                    # into a path component (i.e. "ref/models").
                    path = json_built_dir.rel_path_to(built_doc)
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
                            title = unescape_entities(strip_tags(json_doc['title']))
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

    def update_git(self, url, destdir):
        if '@' in url:
            repo, branch = url.rsplit('@', 1)
        else:
            repo, branch = url, 'master'
        if destdir.child('.git').exists():
            try:
                cwd = os.getcwdu()
                os.chdir(destdir)
                subprocess.call(['git', 'reset', '--hard', 'HEAD'])
                subprocess.call(['git', 'pull'])
            finally:
                os.chdir(cwd)
        else:
            subprocess.call(['git', 'clone', '-q', '--branch', branch, repo, destdir])
