import sys
import tempfile
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import ANY, MagicMock, patch

from django.core.management import CommandError
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


class BuildDocReleaseSphinxErrorTests(TestCase):
    def setUp(self):
        self.release = DocumentRelease.objects.create(lang="en", release=None)
        self.command = Command()
        self.command.verbosity = 0

    def test_sphinx_error_raises_command_error_and_reports_to_sentry(self):
        with tempfile.TemporaryDirectory() as tmp:
            # This will fail: {tmp}/sources/dev/docs/conf.py doesn't exist.
            with (
                override_settings(DOCS_BUILD_ROOT=Path(tmp)),
                patch.object(Command, "_html_builder_name", return_value="html"),
                patch(
                    "docs.management.commands.build_doc_release."
                    "capture_sentry_exception"
                ) as mock_capture,
            ):
                with self.assertRaisesMessage(
                    CommandError, "run-sphinx.py returned an error"
                ) as caught:
                    self.command.build_doc_release(self.release)
                self.assertRegex(
                    str(caught.exception),
                    r"FileNotFoundError.*sources/dev/docs/conf\.py",
                )

        mock_capture.assert_called_once_with(ANY, flush=True)
        self.assertIsInstance(mock_capture.call_args.args[0], CalledProcessError)


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
