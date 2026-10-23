import sys
import tempfile
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import ANY, MagicMock, patch

from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings

from ..management.commands.build_doc_release import Command
from ..management.commands.update_docs import Command as UpdateDocsCommand
from ..models import DocumentRelease


class HtmlBuilderNameTests(TestCase):
    def setUp(self):
        self.command = Command()

    def test_returns_djangohtml_when_registered_by_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp)
            ext_dir = source_dir / "_ext"
            ext_dir.mkdir()
            (ext_dir / "djangodocs.py").write_text('BUILDER = "djangohtml"\n')
            self.assertEqual(self.command._html_builder_name(source_dir), "djangohtml")

    def test_returns_html_when_djangohtml_not_registered(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp)
            ext_dir = source_dir / "_ext"
            ext_dir.mkdir()
            (ext_dir / "djangodocs.py").write_text("# nothing special here\n")
            self.assertEqual(self.command._html_builder_name(source_dir), "html")


class EnsureBuilderExtensionTests(TestCase):
    def setUp(self):
        self.command = Command()

    def test_appends_extensions_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            conf_path = Path(tmp) / "conf.py"
            conf_path.write_text("extensions = ['sphinx.ext.autodoc']\n")
            self.command._add_custom_extension(conf_path)
            content = conf_path.read_text()
            self.assertIn(
                'extensions.append("python_objects_json_html_builder")', content
            )

    def test_idempotent_on_subsequent_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            conf_path = Path(tmp) / "conf.py"
            conf_path.write_text("extensions = ['sphinx.ext.autodoc']\n")
            self.command._add_custom_extension(conf_path)
            first_content = conf_path.read_text()
            self.command._add_custom_extension(conf_path)
            second_content = conf_path.read_text()
            self.assertEqual(first_content, second_content)
            self.assertEqual(
                second_content.count(
                    'extensions.append("python_objects_json_html_builder")'
                ),
                1,
            )


class BuildDocReleaseSphinxErrorTests(TestCase):
    def setUp(self):
        DocumentRelease.objects.create(lang="en", release=None)

    def test_sphinx_error_raises_command_error_and_reports_to_sentry(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = Path(tmp) / "sources" / "dev" / "docs"
            docs_dir.mkdir(parents=True)
            (docs_dir / "conf.py").write_text('extensions = ["unknown_extension"]\n')
            with (
                override_settings(DOCS_BUILD_ROOT=Path(tmp)),
                patch.object(Command, "_html_builder_name", return_value="html"),
                patch(
                    "docs.management.commands.build_doc_release."
                    "capture_sentry_exception"
                ) as mock_capture,
            ):
                with self.assertRaisesMessage(
                    CommandError, "sphinx-build returned an error"
                ) as caught:
                    call_command(
                        "build_doc_release", "dev", "--language", "en", verbosity=0
                    )
                self.assertIn(
                    "Could not import extension unknown_extension",
                    str(caught.exception),
                )

        mock_capture.assert_called_once_with(ANY, flush=True)
        reported = mock_capture.call_args.args[0]
        self.assertIsInstance(reported, CommandError)
        self.assertIsInstance(reported.__cause__, CalledProcessError)


class BuildReleaseSubprocessInvocationTests(TestCase):
    def test_invokes_child_via_module_flag_not_sys_argv(self):
        release = DocumentRelease.objects.create(lang="en", release=None)
        command = UpdateDocsCommand()
        command.verbosity = 2

        with patch("docs.management.commands.update_docs.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            command._build_release_in_subprocess(release)

        mock_run.assert_called_once_with(
            [
                sys.executable,
                "-m",
                "django",
                "build_doc_release",
                "dev",
                "--language",
                "en",
                "--verbosity",
                "2",
            ]
        )


class UpdateDocsResilienceTests(TestCase):
    def test_one_release_failure_does_not_abort_remaining_releases(self):
        failing_release = DocumentRelease.objects.create(lang="en", release=None)
        other_release = DocumentRelease.objects.create(lang="fr", release=None)
        error = RuntimeError("boom")
        attempted = []

        def fake_build_doc_release(release, force=False, interactive=False):
            attempted.append(release)
            if release == failing_release:
                raise error

        command = UpdateDocsCommand()

        with (
            patch.object(
                UpdateDocsCommand,
                "_get_doc_releases",
                return_value=[failing_release, other_release],
            ),
            patch.object(
                UpdateDocsCommand,
                "build_doc_release",
                side_effect=fake_build_doc_release,
            ),
            patch(
                "docs.management.commands.update_docs.capture_sentry_exception"
            ) as mock_capture,
        ):
            command.handle(
                force=False, interactive=False, purge_cache=False, verbosity=0
            )

        self.assertEqual(attempted, [failing_release, other_release])
        mock_capture.assert_called_once_with(error, flush=True)


class BuildDocReleaseStorageTests(TestCase):
    def setUp(self):
        self.release = DocumentRelease.objects.create(lang="en", release=None)
        self.command = Command()
        self.command.verbosity = 0

    def test_build_doc_release_uses_default_storage(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sources_dir = tmp_path / "sources" / "dev" / "docs"
            sources_dir.mkdir(parents=True)
            (sources_dir / "conf.py").write_text("extensions = []\n")

            build_dir = tmp_path / "en" / "dev" / "_build" / "html"
            build_dir.mkdir(parents=True)
            (build_dir / "index.html").write_text("<h1>Docs</h1>")

            with (
                override_settings(DOCS_BUILD_ROOT=tmp_path),
                patch.object(Command, "_html_builder_name", return_value="html"),
                patch("docs.management.commands.build_doc_release.Sphinx"),
                patch("docs.management.commands.build_doc_release.patch_docutils"),
                patch("docs.management.commands.build_doc_release.docutils_namespace"),
                patch(
                    "docs.management.commands.build_doc_release.subprocess.check_call"
                ),
                patch.object(DocumentRelease, "sync_to_db"),
                patch(
                    "docs.management.commands.build_doc_release.default_storage"
                ) as mock_storage,
            ):
                self.command.build_doc_release(self.release)

                mock_storage.save.assert_called_once()
                saved_name = mock_storage.save.call_args[0][0]
                self.assertEqual(
                    saved_name,
                    f"docs/django-docs-{self.release.version}-{self.release.lang}.zip",
                )
