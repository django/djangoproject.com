import io
import os
import re
from pathlib import Path
from unittest import skipUnless

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch
from playwright.sync_api import sync_playwright

from djangoproject.tests import ReleaseMixin
from djangoproject.urls.www import sitemaps

from .settings.dev import HOST_SCHEME, PARENT_HOST

working_dir = (
    Path(__file__).parent.joinpath(os.environ["SCREENSHOT_DIR"])
    if "SCREENSHOT_DIR" in os.environ
    else Path(__file__).parent.joinpath("tests", "screenshots")
)

themes = (
    [s.strip() for s in os.environ["SCREENSHOT_THEMES"].split(",")]
    if "SCREENSHOT_THEMES" in os.environ
    else ["dark", "light"]
)

widths = (
    [int(x) for x in os.environ["SCREENSHOT_WIDTHS"].split(",")]
    if "SCREENSHOT_WIDTHS" in os.environ
    else [
        414,
        768,
        1366,
    ]  # https://www.browserstack.com/guide/common-screen-resolutions
)


class GenerateScreenshotMixin:
    def generateScreenshot(self, location, page, variant, *, threshold=0.1):
        # Derive a friendly test name from the URL
        tokens = [f"{HOST_SCHEME}://", f".{PARENT_HOST}"]
        pattern = "|".join(map(re.escape, tokens))
        *_, subdomain, path = re.split(pattern, location)
        screen_name = f"{subdomain} {re.sub(r'/', ' ', path).strip()}"
        screen_name = re.sub(r"\s", "_", screen_name)

        # Keep two baselines - one we keep frozen on disk to compare with, and
        # another to show to the user which we may modify to match image
        # dimensions.
        frozen_baseline_path = self._frozen_path(screen_name, variant, "baseline.png")
        baseline_path = self._path(screen_name, variant, "baseline.png")
        current_path = self._path(screen_name, variant, "current.png")
        diff_path = self._path(screen_name, variant, "diff.png")

        frozen_baseline_path.parent.mkdir(parents=True, exist_ok=True)

        # Clean up first to avoid signalling any ambiguous test results.
        if current_path.exists():
            os.remove(current_path)
        if diff_path.exists():
            os.remove(diff_path)

        page.goto(location)
        page.wait_for_timeout(500)
        screenshot_bytes = page.screenshot(full_page=True)

        if os.environ["SCREENSHOT_MODE"] == "baseline":
            baseline = Image.open(io.BytesIO(screenshot_bytes))
            baseline.save(frozen_baseline_path)
            return (None, None)
        elif not frozen_baseline_path.exists():
            return (
                None,
                f"Skipped {'/'.join([screen_name, *variant])}, baseline "
                "screenshot does not exist",
            )

        current = Image.open(io.BytesIO(screenshot_bytes))

        baseline = Image.open(frozen_baseline_path)
        if baseline.size != current.size:
            # Resize both to the largest of both dimensions to enable
            # comparison.
            max_width = max(baseline.size[0], current.size[0])
            max_height = max(baseline.size[1], current.size[1])
            if max_width != baseline.size[0] or max_height != baseline.size[1]:
                canvas = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 255))
                canvas.paste(baseline, (0, 0))
                baseline = canvas
            if max_width != current.size[0] or max_height != current.size[1]:
                canvas = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 255))
                canvas.paste(current, (0, 0))
                current = canvas

        diff = Image.new("RGBA", baseline.size)
        diff_ratio = pixelmatch(current, baseline, diff)
        if diff_ratio > 0:
            baseline_path.parent.mkdir(parents=True, exist_ok=True)
            baseline.save(baseline_path)
            current.save(current_path)
            diff.save(diff_path)
            return (f"Differences in {'/'.join([screen_name, *variant])}", None)

        return (None, None)

    def _frozen_path(self, screen_name, variant, name):
        return Path().joinpath(working_dir, "baseline", screen_name, *variant, name)

    def _path(self, screen_name, variant, name):
        return Path().joinpath(working_dir, screen_name, *variant, name)


@skipUnless(
    "SCREENSHOT_MODE" in os.environ,
    "Set SCREENSHOT_MODE=baseline or compare to generate before and after screenshots.",
)
class ScreenshotTests(ReleaseMixin, GenerateScreenshotMixin, StaticLiveServerTestCase):
    fixtures = ["doc_releases", "dashboard_test_data"]
    port = 8000

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()
        cls.mac_user_agent = "Mozilla/5.0 (Macintosh) AppleWebKit"
        cls.windows_user_agent = "Mozilla/5.0 (Windows NT 10.0)"
        cls.mobile_linux_user_agent = "Mozilla/5.0 (Linux; Android 10; Mobile)"

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        super().setUp()
        self.setUpTestData()

    def test_screenshots(self):
        diffs = []
        skipped = []

        diff_list_path = Path.joinpath(working_dir, "diffs.txt")
        skipped_list_path = Path.joinpath(working_dir, "skipped.txt")

        # Clean up first to avoid signalling any ambiguous test results.
        if diff_list_path.exists():
            os.remove(diff_list_path)
        if skipped_list_path.exists():
            os.remove(skipped_list_path)

        for sitemap in sitemaps.values():
            for location in [url.get("location") for url in sitemap().get_urls()]:
                page = self.browser.new_page(user_agent=self.mac_user_agent)
                self.browser.browser_type.name
                for theme in themes:
                    page.context.add_cookies(
                        [
                            {
                                "name": "theme",
                                "value": theme,
                                "domain": "localhost",
                                "path": "/",
                            }
                        ]
                    )
                    for width in widths:
                        page.set_viewport_size({"width": width, "height": 800})
                        variant = [self.browser.browser_type.name, theme, str(width)]

                        diff, skip = self.generateScreenshot(location, page, variant)
                        if diff:
                            diffs.append(diff)
                        if skip:
                            skipped.append(skip)

        if len(diffs) > 0:
            with open(diff_list_path, "w") as f:
                f.write("\n".join(diffs))
                f.write("\n")

        if len(skipped) > 0:
            with open(skipped_list_path, "w") as f:
                f.write("\n".join(skipped))
                f.write("\n")
