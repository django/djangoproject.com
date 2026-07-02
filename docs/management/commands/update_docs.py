"""
Update and build the documentation into files for display with the djangodocs
app.
"""

import os
import subprocess
import sys
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db.models import Q

from ...models import DocumentRelease
from ...utils import capture_sentry_exception


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

        # Keep track of which Git sources have been updated, e.g.,
        # {'1.8': True} if the 1.8 docs updated.
        self.release_docs_changed = {}

        for release in self._get_doc_releases(versions, kwargs):
            try:
                self.build_doc_release(
                    release, force=kwargs["force"], interactive=kwargs["interactive"]
                )
            except Exception as e:
                capture_sentry_exception(e, flush=True)
                self.stderr.write(
                    f"build_doc_release failed for {release}, skipping: {e}"
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

        release.sync_from_sitemap(force=force)

        # checkout_dir is shared for all languages.
        checkout_dir = settings.DOCS_BUILD_ROOT / "sources" / release.version
        if not checkout_dir.exists():
            checkout_dir.mkdir(parents=True)

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

        self._build_release_in_subprocess(release)

    def _build_release_in_subprocess(self, release):
        """Build a single release's docs in a fresh subprocess.

        Each release is built in its own process (rather than in-process,
        looping over every release here) because docs/_ext/djangodocs.py is
        loaded by dynamically appending the checkout's docs/_ext directory
        to sys.path and importing it by bare module name. Building multiple
        checkouts in one Python process lets a later checkout's import of
        that same module name silently reuse an earlier, different
        checkout's already-cached module instead of its own.
        """
        command = [
            sys.executable,
            sys.argv[0],
            "build_doc_release",
            release.version,
            "--language",
            release.lang,
            "--verbosity",
            str(self.verbosity),
        ]

        result = subprocess.run(command)
        if result.returncode != 0:
            self.stderr.write(
                "build_doc_release subprocess failed for %s (exit code %s)"
                % (release, result.returncode)
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
