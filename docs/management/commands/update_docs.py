"""
Update and build the documentation into files for display with the djangodocs
app.
"""
import json
import os
import shutil
import subprocess
import zipfile
from contextlib import closing
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import to_locale

from ...models import DocumentRelease


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-indexing',
            action='store_false',
            dest='reindex',
            default=True,
            help='Skip reindexing (for testing, mostly).'
        )

    def handle(self, **kwargs):
        verbosity = kwargs['verbosity']

        default_builders = ['json', 'html']
        default_docs_version = DocumentRelease.objects.get(is_default=True).release.version

        # Keep track of which Git sources have been updated.
        release_docs_changed = {}  # e.g. {'1.8': True} if the 1.8 docs updated.

        # Somehow, bizarely, there's a bug in Sphinx such that if I try to
        # build 1.0 before other versions, things fail in weird ways. However,
        # building newer versions first works. I suspect Sphinx is hanging onto
        # some global state. Anyway, we can work around it by making sure that
        # "dev" builds before "1.0". This is ugly, but oh well.
        for release in DocumentRelease.objects.order_by('-release'):
            if verbosity >= 1:
                self.stdout.write("Updating %s..." % release)

            # checkout_dir is shared for all languages.
            checkout_dir = settings.DOCS_BUILD_ROOT.joinpath('sources', release.version)
            parent_build_dir = settings.DOCS_BUILD_ROOT.joinpath(release.lang, release.version)
            if not checkout_dir.exists():
                checkout_dir.mkdir(parents=True)
            if not parent_build_dir.exists():
                parent_build_dir.mkdir(parents=True)

            #
            # Update the release from SCM.
            #
            # Make a git checkout/update into the destination directory.
            if (not self.update_git(release.scm_url, checkout_dir, changed_dir='docs/') and
                    not release_docs_changed.get(release.version)):
                # No docs changes so don't rebuild.
                continue

            release_docs_changed[release.version] = True

            source_dir = checkout_dir.joinpath('docs')

            if release.lang != 'en':
                # Skip translated non-stable versions to avoid a crash:
                # https://github.com/django/djangoproject.com/issues/627
                if not release.release.version == default_docs_version:
                    continue
                scm_url = release.scm_url.replace('django.git', 'django-docs-translations.git')
                trans_dir = checkout_dir.joinpath('django-docs-translation')
                if not trans_dir.exists():
                    trans_dir.mkdir()
                self.update_git(scm_url, trans_dir)
                if not source_dir.joinpath('locale').exists():
                    source_dir.joinpath('locale').symlink_to(trans_dir.joinpath('translations'))
                subprocess.call("cd %s && make translations" % trans_dir, shell=True)

            if release.is_default:
                # Build the pot files (later retrieved by Transifex)
                builders = default_builders[:] + ['gettext']
            else:
                builders = default_builders

            #
            # Use Sphinx to build the release docs into JSON and HTML documents.
            #
            for builder in builders:
                # Wipe and re-create the build directory. See #18930.
                build_dir = parent_build_dir.joinpath('_build', builder)
                if build_dir.exists():
                    shutil.rmtree(str(build_dir))
                build_dir.mkdir(parents=True)

                if verbosity >= 2:
                    self.stdout.write("  building %s (%s -> %s)" % (builder, source_dir, build_dir))
                subprocess.check_call([
                    'sphinx-build',
                    '-b', builder,
                    '-D', 'language=%s' % to_locale(release.lang),
                    '-q',              # Be vewy qwiet
                    str(source_dir),        # Source file directory
                    str(build_dir),         # Destination directory
                ])

            #
            # Create a zip file of the HTML build for offline reading.
            # This gets moved into MEDIA_ROOT for downloading.
            #
            html_build_dir = parent_build_dir.joinpath('_build', 'html')
            zipfile_name = 'django-docs-%s-%s.zip' % (release.version, release.lang)
            zipfile_path = Path(settings.MEDIA_ROOT).joinpath('docs', zipfile_name)
            if not zipfile_path.parent.exists():
                zipfile_path.parent.mkdir(parents=True)
            if verbosity >= 2:
                self.stdout.write("  build zip (into %s)" % zipfile_path)

            def zipfile_inclusion_filter(file_path):
                return '.doctrees' not in file_path.parts

            with closing(zipfile.ZipFile(str(zipfile_path), 'w', compression=zipfile.ZIP_DEFLATED)) as zf:
                for root, dirs, files in os.walk(str(html_build_dir)):
                    for f in files:
                        file_path = Path(os.path.join(root, f))
                        if zipfile_inclusion_filter(file_path):
                            rel_path = str(file_path.relative_to(html_build_dir))
                            zf.write(str(file_path), rel_path)

            #
            # Copy the build results to the directory used for serving
            # the documentation in the least disruptive way possible.
            #
            build_dir = parent_build_dir.joinpath('_build')
            built_dir = parent_build_dir.joinpath('_built')
            subprocess.check_call([
                'rsync',
                '--archive',
                '--delete',
                '--link-dest={}'.format(build_dir),
                '{}/'.format(build_dir),
                str(built_dir)
            ])

            #
            # Rebuild the imported document list and search index.
            #
            if not kwargs['reindex']:
                continue

            if verbosity >= 2:
                self.stdout.write("  reindexing...")

            json_built_dir = parent_build_dir.joinpath('_built', 'json')
            documents = gen_decoded_documents(json_built_dir)
            release.sync_to_db(documents)

    def update_git(self, url, destdir, changed_dir='.'):
        """
        Update a source checkout and return True if any docs were changed,
        False otherwise.
        """
        if '@' in url:
            repo, branch = url.rsplit('@', 1)
        else:
            repo, branch = url, 'master'
        if destdir.joinpath('.git').exists():
            remote = 'origin'
            branch_with_remote = '%s/%s' % (remote, branch)
            try:
                cwd = os.getcwd()
                os.chdir(str(destdir))
                subprocess.call(['git', 'reset', '--hard', 'HEAD'])
                subprocess.call(['git', 'clean', '-fdx'])
                subprocess.call([
                    'git', 'fetch', remote,
                    '%s:refs/remotes/%s' % (branch, branch_with_remote)
                ])
                docs_changed = subprocess.call([
                    'git', 'diff', branch_with_remote,
                    '--quiet', '--exit-code',
                    changed_dir,
                ]) == 1
                if not docs_changed:
                    return False
                subprocess.call(['git', 'merge', branch_with_remote])
            finally:
                os.chdir(cwd)
        else:
            subprocess.call(['git', 'clone', '-q', '--branch', branch, repo, str(destdir)])
        return True


def gen_decoded_documents(directory):
    """
    Walk the given directory looking for fjson files and yield their data.
    """
    for root, dirs, files in os.walk(str(directory)):
        for f in files:
            f = Path(root, f)
            if not f.suffix == '.fjson':
                continue

            with f.open() as fp:
                yield json.load(fp)
