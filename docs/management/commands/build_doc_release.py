"""Build the documentation for a single release (version + language).

This command is meant to be invoked as a subprocess by `update_docs`, one
process per release. `update_docs` builds many releases across Django versions
in a single run, and in some checkouts, `docs/_ext/djangodocs.py` dynamically
sys.path-append their own `_ext` directory and import extension modules (e.g.
"djangodocs", "github_links") by bare name. Building all releases in one Python
process let a newer checkout's already-imported module get silently reused for
an older checkout's build later in the same run. A fresh process per release
avoids that class of bug entirely.

`update_docs` is responsible for syncing the release's git checkout (shared
across a version's languages) before invoking this command; this command
assumes the checkout is already up to date and only builds it.

"""

import json
import multiprocessing
import os
import shutil
import subprocess
import sys
import zipfile
from contextlib import closing
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.utils.translation import to_locale
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.errors import SphinxError
from sphinx.testing.util import _clean_up_global_state
from sphinx.util.docutils import docutils_namespace, patch_docutils

from ...models import DocumentRelease
from ...utils import capture_sentry_exception


class Command(BaseCommand):
    help = (
        "Build the docs for a single release (version + language). Intended "
        "to be invoked as a subprocess by update_docs, one process per "
        "release, once its git checkout is already up to date."
    )

    def add_arguments(self, parser):
        parser.add_argument("version", help="Which version to build (e.g. 6.0, dev)")
        parser.add_argument(
            "--language", required=True, help="Language code of the release to build"
        )

    def handle(self, version, **options):
        self.verbosity = options["verbosity"]
        try:
            release = DocumentRelease.objects.get_by_version_and_lang(
                version, options["language"]
            )
        except DocumentRelease.DoesNotExist:
            raise CommandError(
                "No DocumentRelease found for version=%r lang=%r"
                % (version, options["language"])
            )

        self.build_doc_release(release)

    def _html_builder_name(self, source_dir):
        """Return the Sphinx builder name to use for HTML output for a given
        checkout.

        Older Django versions' docs/_ext/djangodocs.py registers a custom
        "djangohtml" builder. Django's #37150 cleanup removed it in favor of
        hooking into any HTML-format builder, including the standard "html"
        builder, but that cleanup isn't backported to branches that predate
        it (e.g. 6.0, 5.2), so "djangohtml" must still be requested there.
        """
        djangodocs_path = source_dir / "_ext" / "djangodocs.py"
        if '"djangohtml"' in djangodocs_path.read_text():
            return "djangohtml"
        return "html"

    def build_doc_release(self, release):
        """Build the docs for a single release.

        The release's git checkout is assumed to already be up to date.
        """
        # checkout_dir is shared for all languages.
        checkout_dir = settings.DOCS_BUILD_ROOT / "sources" / release.version
        parent_build_dir = settings.DOCS_BUILD_ROOT / release.lang / release.version
        if not parent_build_dir.exists():
            parent_build_dir.mkdir(parents=True)

        source_dir = checkout_dir / "docs"

        html_builder = self._html_builder_name(source_dir)
        builders = ["json", html_builder]
        if release.is_default:
            # Build the pot files (later retrieved by Transifex)
            builders.append("gettext")

        #
        # Use Sphinx to build the release docs into JSON and HTML documents.
        #
        for builder in builders:
            # Wipe and re-create the build directory. See #18930.
            build_dir = parent_build_dir / "_build" / builder
            if build_dir.exists():
                shutil.rmtree(str(build_dir))
            build_dir.mkdir(parents=True)

            if self.verbosity >= 2:
                self.stdout.write(f"  building {builder} ({source_dir} -> {build_dir})")
            # Retrieve the extensions from the conf.py so we can append to them.
            conf_extensions = Config.read(source_dir.resolve()).extensions
            extensions = [*conf_extensions, "docs.builder"]
            try:
                # Prevent global state persisting between builds
                # https://github.com/sphinx-doc/sphinx/issues/12130
                with patch_docutils(source_dir), docutils_namespace():
                    Sphinx(
                        srcdir=source_dir,
                        confdir=source_dir,
                        outdir=build_dir,
                        doctreedir=build_dir / ".doctrees",
                        buildername=builder,
                        # Translated docs builds generate a lot of warnings, so send
                        # stderr to stdout to be logged (rather than generating an email)
                        warning=sys.stdout,
                        parallel=multiprocessing.cpu_count(),
                        verbosity=0,
                        confoverrides={
                            "language": to_locale(release.lang),
                            "extensions": extensions,
                        },
                    ).build()
                # Clean up global state after building each language.
                _clean_up_global_state()
            except SphinxError as e:
                capture_sentry_exception(e, flush=True)
                raise CommandError(
                    "sphinx-build returned an error (release %s, builder %s): %s"
                    % (release, builder, str(e))
                ) from e

        #
        # Create a zip file of the HTML build for offline reading.
        # This gets moved into MEDIA_ROOT for downloading.
        #
        html_build_dir = parent_build_dir / "_build" / html_builder
        zipfile_name = f"django-docs-{release.version}-{release.lang}.zip"
        zipfile_path = settings.MEDIA_ROOT / "docs" / zipfile_name
        if not zipfile_path.parent.exists():
            zipfile_path.parent.mkdir(parents=True)
        if self.verbosity >= 2:
            self.stdout.write("  build zip (into %s)" % zipfile_path)

        def zipfile_inclusion_filter(file_path):
            return ".doctrees" not in file_path.parts

        with closing(
            zipfile.ZipFile(str(zipfile_path), "w", compression=zipfile.ZIP_DEFLATED)
        ) as zf:
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
        build_dir = parent_build_dir / "_build"
        built_dir = parent_build_dir / "_built"
        subprocess.check_call(
            [
                "rsync",
                "--archive",
                "--delete",
                f"--link-dest={build_dir}",
                f"{build_dir}/",
                str(built_dir),
            ]
        )

        if release.is_default:
            self._setup_stable_symlink(release, built_dir)

        json_built_dir = parent_build_dir / "_built" / "json"
        documents = gen_decoded_documents(json_built_dir)
        release.sync_to_db(documents)

    def _setup_stable_symlink(self, release, built_dir):
        """
        Setup a symbolic link called "stable" pointing to the given release build
        """
        stable = built_dir / "stable"
        target = built_dir / release.version
        if stable.resolve() != target:  # Symlink is either missing or has changed
            stable.unlink(missing_ok=True)
            stable.symlink_to(target, target_is_directory=True)


def gen_decoded_documents(directory):
    """
    Walk the given directory looking for fjson files and yield their data.
    """
    for root, dirs, files in os.walk(str(directory)):
        for f in files:
            f = Path(root, f)
            if not f.suffix == ".fjson":
                continue

            with f.open() as fp:
                yield json.load(fp)
