"""
Update and build the documentation into files for display with the djangodocs
app.
"""

import json

# import multiprocessing
import os
import shutil
import subprocess
import sys
import zipfile
from contextlib import closing
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db.models import Q
from django.utils.translation import to_locale

# from sphinx.application import Sphinx
from sphinx.config import Config

from ...models import DocumentRelease

# from sphinx.errors import SphinxError
# from sphinx.testing.util import _clean_up_global_state
# from sphinx.util.docutils import docutils_namespace, patch_docutils



class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--language",
            help="Only build docs for this specific language",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help=(
                "Force docs update even if docs in git didn't change or the "
                "version is no longer supported."
            ),
        )
        parser.add_argument(
            "--interactive",
            action="store_true",
            help="Ask before building each version",
        )
        parser.add_argument(
            "--purge-cache",
            action="store_true",
            dest="purge_cache",
            default=False,
            help="Also invalidate downstream caches for any changed doc versions.",
        )
        parser.add_argument(
            "args",
            metavar="versions",
            nargs="*",
            help="Which version to rebuild (all by default)",
        )

    def _get_doc_releases(self, versions, options):
        """
        Return a DocumentRelease queryset of all the versions that should be
        built, based on the arguments received on the command line.
        """
        default_docs_version = DocumentRelease.objects.get(
            is_default=True
        ).release.version

        # Somehow, bizarely, there's a bug in Sphinx such that if I try to
        # build 1.0 before other versions, things fail in weird ways. However,
        # building newer versions first works. I suspect Sphinx is hanging onto
        # some global state. Anyway, we can work around it by making sure that
        # "dev" builds before "1.0". This is ugly, but oh well.
        queryset = DocumentRelease.objects.order_by("-release")

        # Skip translated non-stable versions to avoid a crash:
        # https://github.com/django/djangoproject.com/issues/627
        queryset = queryset.filter(
            Q(lang=settings.DEFAULT_LANGUAGE_CODE) | Q(release=default_docs_version)
        )

        if options["language"]:
            queryset = queryset.filter(lang=options["language"])

        if versions:
            queryset = queryset.by_versions(*versions)

        return queryset

    def handle(self, *versions, **kwargs):
        self.verbosity = kwargs["verbosity"]
        self.purge_cache = kwargs["purge_cache"]

        self.default_builders = ["json", "djangohtml"]

        # Keep track of which Git sources have been updated, e.g.,
        # {'1.8': True} if the 1.8 docs updated.
        self.release_docs_changed = {}

        for release in self._get_doc_releases(versions, kwargs):
            self.build_doc_release(
                release, force=kwargs["force"], interactive=kwargs["interactive"]
            )

        if self.purge_cache:
            changed_versions = {
                version
                for version, changed in self.release_docs_changed.items()
                if changed
            }
            if changed_versions or kwargs["force"]:
                call_command(
                    "purge_docs_cache",
                    **{"doc_versions": changed_versions, "verbosity": self.verbosity},
                )
            else:
                if self.verbosity >= 1:
                    self.stdout.write("No docs changes; skipping cache purge.")

    def build_doc_release(self, release, force=False, interactive=False):
        # Skip not supported releases.
        if not release.is_supported and not force:
            return
        if interactive:
            prompt = (
                f"About to start building docs for release {release}. Continue? Y/n "
            )
            if input(prompt).upper() not in {"", "Y", "YES", "OUI"}:
                return
        if self.verbosity >= 1:
            self.stdout.write(f"Starting update for {release} at {datetime.now()}...")

        # checkout_dir is shared for all languages.
        checkout_dir = settings.DOCS_BUILD_ROOT / "sources" / release.version
        parent_build_dir = settings.DOCS_BUILD_ROOT / release.lang / release.version
        if not checkout_dir.exists():
            checkout_dir.mkdir(parents=True)
        if not parent_build_dir.exists():
            parent_build_dir.mkdir(parents=True)

        #
        # Update the release from SCM.
        #
        # Make a git checkout/update into the destination directory.
        git_changed = self.update_git(
            release.scm_url, checkout_dir, changed_dir="docs/"
        )
        if git_changed:
            self.release_docs_changed[release.version] = True
        version_changed = git_changed or self.release_docs_changed.get(release.version)
        if not force and not version_changed:
            if self.verbosity >= 1:
                self.stdout.write(
                    "No docs changes for %s, skipping docs building." % release
                )
            return

        source_dir = checkout_dir / "docs"

        if release.lang != settings.DEFAULT_LANGUAGE_CODE:
            scm_url = release.scm_url.replace(
                "django.git", "django-docs-translations.git"
            )
            trans_dir = checkout_dir / "django-docs-translation"
            if not trans_dir.exists():
                trans_dir.mkdir()
            self.update_git(scm_url, trans_dir)

            locale_dir = source_dir / "locale"
            if not locale_dir.exists():
                locale_dir.symlink_to(trans_dir / "translations")

            extra_kwargs = {"stdout": subprocess.DEVNULL} if self.verbosity == 0 else {}
            subprocess.check_call(
                "cd %s && make translations" % trans_dir, shell=True, **extra_kwargs
            )

        if release.is_default:
            # Build the pot files (later retrieved by Transifex)
            builders = self.default_builders[:] + ["gettext"]
        else:
            builders = self.default_builders

        #
        # Use Sphinx to build the release docs into JSON and HTML documents.
        #
        for builder in builders:
            build_dir = parent_build_dir / "_build" / builder
            if build_dir.exists():
                shutil.rmtree(build_dir)
            build_dir.mkdir(parents=True)

            doctreedir = parent_build_dir / "_doctrees" / release.lang / builder
            if doctreedir.exists():
                shutil.rmtree(doctreedir)
            doctreedir.mkdir(parents=True)

            conf_extensions = Config.read(source_dir.resolve()).extensions
            extensions = ",".join([*conf_extensions, "docs.builder"])

            try:
                self.run_sphinx_build(
                    source_dir=source_dir,
                    build_dir=build_dir,
                    doctreedir=doctreedir,
                    builder=builder,
                    language=to_locale(release.lang),
                    extensions=extensions,
                )
            except subprocess.CalledProcessError as e:
                self.stderr.write(
                    f"sphinx-build failed (release={release}, builder={builder}): {e}"
                )
                return

        #
        # Create a zip file of the HTML build for offline reading.
        # This gets moved into MEDIA_ROOT for downloading.
        #
        html_build_dir = parent_build_dir / "_build" / "djangohtml"
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

        def run_sphinx_build(
            self,
            *,
            source_dir,
            build_dir,
            doctreedir,
            builder,
            language,
            extensions,
        ):
            env = os.environ.copy()
            env["SPHINXOPTS"] = " ".join(
                [
                    f"-D language={language}",
                    f"-D extensions={extensions}",
                ]
            )
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "sphinx",
                    "-b",
                    builder,
                    "-c",
                    str(source_dir),
                    "-d",
                    str(doctreedir),
                    str(source_dir),
                    str(build_dir),
                ],
                env=env,
            )

    def update_git(self, url, destdir, changed_dir="."):
        """
        Update a source checkout and return True if any docs were changed,
        False otherwise.
        """
        quiet = "--quiet" if self.verbosity == 0 else "--"
        if "@" in url:
            repo, branch = url.rsplit("@", 1)
        else:
            repo, branch = url, "main"
        if (destdir / ".git").exists():
            remote = "origin"
            branch_with_remote = f"{remote}/{branch}"
            try:
                cwd = os.getcwd()
                os.chdir(str(destdir))
                # Git writes all output to stderr, so redirect it to stdout for
                # logging (so we don't get emailed with all Git output).
                subprocess.check_call(
                    ["git", "reset", "--hard", "HEAD", quiet], stderr=sys.stdout
                )
                subprocess.check_call(
                    ["git", "clean", "-fdx", quiet], stderr=sys.stdout
                )
                subprocess.check_call(
                    [
                        "git",
                        "fetch",
                        remote,
                        f"{branch}:refs/remotes/{branch_with_remote}",
                        quiet,
                    ],
                    stderr=sys.stdout,
                )
                docs_changed = (
                    subprocess.call(
                        [
                            "git",
                            "diff",
                            branch_with_remote,
                            "--quiet",
                            "--exit-code",
                            changed_dir,
                        ],
                        stderr=sys.stdout,
                    )
                    == 1
                )
                if not docs_changed:
                    return False
                subprocess.check_call(
                    ["git", "merge", branch_with_remote, quiet], stderr=sys.stdout
                )
            finally:
                os.chdir(cwd)
        else:
            subprocess.check_call(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    branch,
                    repo,
                    str(destdir),
                    quiet,
                ],
                stderr=sys.stdout,
            )
        return True

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
