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
assumes the checkout is already up to date, and appends the website's custom
builder to the checkout's `docs/conf.py`.

"""

import json
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

        try:
            self.build_doc_release(release)
        except Exception as e:
            # update_docs runs this command in a subprocess and only logs the
            # exit code, so failures have to be reported from here to reach
            # Sentry at all.
            capture_sentry_exception(e, flush=True)
            raise

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

    def _add_custom_extension(self, conf_path):
        """Add djangoproject.com custom Sphinx builder extension to conf.py.

        Add the website's custom builder in the conf.py file if it isn't
        already there. (This cannot be handled with ``sphinx-build --define
        extensions=...`` because that would override the existing extensions.)

        This writes to the checked out conf.py file. `update_docs.update_git()`
        resets and cleans the checkout before every sync, so the appended line
        neither accumulates nor blocks the merge.
        """
        content = conf_path.read_text(encoding="utf-8")
        content_to_add = 'extensions.append("python_objects_json_html_builder")'
        if content_to_add not in content:
            with conf_path.open("a", encoding="utf-8") as f:
                f.write(f"\n{content_to_add}\n")

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

        # Add djangoproject.com custom Sphinx extensions to the checked out
        # docs/conf.py and make them available for import.
        self._add_custom_extension(source_dir / "conf.py")
        sphinx_ext_dir = str(settings.BASE_DIR / "docs" / "sphinx_ext")
        env = os.environ.copy()
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{sphinx_ext_dir}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = sphinx_ext_dir

        #
        # Use Sphinx to build the release docs into JSON and HTML documents.
        #
        for builder in builders:
            # Wipe and re-create the build directory. See #18930. (This may be
            # unnecessary once a djangodocs extension bug that breaks doctree
            # caching has been fixed in all built versions. #37212#comment:13.)
            build_dir = parent_build_dir / "_build" / builder
            if build_dir.exists():
                shutil.rmtree(str(build_dir))
            build_dir.mkdir(parents=True)
            doctree_dir = build_dir / ".doctrees"

            if self.verbosity >= 2:
                self.stdout.write(f"  building {builder} ({source_dir} -> {build_dir})")
            command = [sys.executable, "-m", "sphinx.cmd.build"]
            command.extend(["--builder", builder])
            command.extend(["--doctree-dir", str(doctree_dir)])
            command.extend(["--jobs", "auto"])
            command.extend(["--define", f"language={to_locale(release.lang)}"])
            command.append(str(source_dir))
            command.append(str(build_dir))
            try:
                result = subprocess.run(
                    command, check=True, stderr=subprocess.PIPE, text=True, env=env
                )
            except subprocess.CalledProcessError as e:
                stderr = e.stderr.strip() if e.stderr else ""
                raise CommandError(
                    f"sphinx-build returned an error (release {release}, "
                    f"builder {builder})\n{e}\nStderr: {stderr}"
                ) from e
            # sphinx-build sends its warnings to stderr, and translated docs
            # builds generate a lot of them. Write them to stdout so they are
            # logged rather than reported as errors.
            if result.stderr:
                self.stdout.write(result.stderr)

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

        json_built_dir = parent_build_dir / "_built" / "json"
        documents = gen_decoded_documents(json_built_dir)
        release.sync_to_db(documents)


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
