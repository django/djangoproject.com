from django.test.runner import DiscoverRunner

#: Playwright browser engines the end-to-end tests can run against.
SUPPORTED_BROWSERS = ["chromium", "firefox", "webkit"]

#: The engines the current run selected. Chromium alone unless ``--browser`` is
#: passed. Read by ``djangoproject.tests.EndToEndTests``; it is module state
#: because there is no other route from a test runner's options into a
#: ``TestCase``.
selected_browsers = ["chromium"]


class BrowserTestRunner(DiscoverRunner):
    """Test runner that lets the end-to-end tests target several browsers.

    ``--browser`` may be repeated::

        python -m manage test --browser chromium --browser firefox

    Chromium alone is the default, so a plain test run costs no more than it
    did before and CI needs no extra browsers installed.
    """

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--browser",
            action="append",
            dest="browsers",
            choices=SUPPORTED_BROWSERS,
            metavar="BROWSER",
            help=(
                "Playwright browser to run the end-to-end tests against; "
                "repeat to use several. Choices: %s. Defaults to chromium."
                % ", ".join(SUPPORTED_BROWSERS)
            ),
        )

    def __init__(self, *args, browsers=None, **kwargs):
        super().__init__(*args, **kwargs)
        # dict.fromkeys de-duplicates while keeping the order given, so
        # `--browser firefox --browser firefox` launches one firefox.
        selected_browsers[:] = list(dict.fromkeys(browsers or ["chromium"]))
