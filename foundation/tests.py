from django.contrib.auth.models import Permission, User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django_hosts.resolvers import reverse

from djangoproject.tests import ReleaseMixin

from .models import Banner


class BannerTestCase(ReleaseMixin, TestCase):
    def test_activating_banner_deactivates_others(self):
        b1 = Banner.objects.create(title="First", is_active=True)
        b2 = Banner.objects.create(title="Second", is_active=True)
        b1.refresh_from_db()
        self.assertIs(b1.is_active, False)
        self.assertIs(b2.is_active, True)

    def test_deactivating_banner_leaves_others_unchanged(self):
        b1 = Banner.objects.create(title="First", is_active=True)
        b2 = Banner.objects.create(title="Second")
        self.assertIs(b2.is_active, False)

        b2.title = "New Title"
        b2.save()
        b1.refresh_from_db()
        self.assertIs(b1.is_active, True)
        b2.refresh_from_db()
        self.assertIs(b2.is_active, False)

    def test_active_banner_tag_no_active_banner(self):
        Banner.objects.create(title="Inactive", is_active=False)
        response = self.client.get("/")
        self.assertNotContains(response, '<div class="banner">')

    def test_active_banner_tag_renders_banner(self):
        Banner.objects.create(
            title="Support Django!",
            body="Please donate.",
            cta_label="Donate",
            cta_url="https://djangoproject.com/donate/",
            is_active=True,
        )
        response = self.client.get("/")
        self.assertContains(response, "<h2>Support Django!</h2>", html=True)
        self.assertContains(response, "Please donate.")
        self.assertContains(
            response,
            '<a id="banner-cta" class="cta" href="https://djangoproject.com/donate/">'
            "Donate</a>",
            html=True,
        )

    def test_cta_label_without_url_raises_validation_error(self):
        banner = Banner(title="Incomplete CTA", cta_label="Click me", cta_url="")
        with self.assertRaisesMessage(
            ValidationError,
            "Both a call-to-action label and URL must be provided, or neither.",
        ):
            banner.full_clean()

    def test_cta_url_without_label_raises_validation_error(self):
        banner = Banner(
            title="Incomplete CTA", cta_label="", cta_url="https://example.com/"
        )
        with self.assertRaisesMessage(
            ValidationError,
            "Both a call-to-action label and URL must be provided, or neither.",
        ):
            banner.full_clean()

    def test_cta_both_fields_set_is_valid(self):
        banner = Banner(
            title="Full CTA",
            cta_label="Click me",
            cta_url="https://example.com/",
        )
        banner.full_clean()

    def test_cta_both_fields_blank_is_valid(self):
        banner = Banner(title="No CTA", cta_label="", cta_url="")
        banner.full_clean()

    def test_active_banner_tag_no_cta_when_fields_blank(self):
        Banner.objects.create(title="No CTA", cta_label="", cta_url="", is_active=True)
        response = self.client.get("/")
        self.assertContains(response, "No CTA")
        self.assertNotContains(response, '<a id="banner-cta" class="cta"')

    def test_inactive_banner_not_shown_on_main_site(self):
        Banner.objects.create(title="Inactive banner", is_active=False)
        response = self.client.get("/")
        self.assertNotContains(response, "Inactive banner")

    def test_banner_get_absolute_url(self):
        banner = Banner.objects.create(title="My Banner")
        self.assertEqual(
            banner.get_absolute_url(),
            reverse("foundation_banner_preview", (banner.pk,)),
        )

    def test_preview_view_requires_login(self):
        banner = Banner.objects.create(title="Draft banner")
        response = self.client.get(banner.get_absolute_url())
        self.assertRedirects(
            response, f"/accounts/login/?next=/foundation/banners/{banner.pk}/preview/"
        )

    def test_preview_view_requires_permission(self):
        banner = Banner.objects.create(title="Draft banner")
        user = User.objects.create_user("viewer", "v@example.com", "password")
        self.client.force_login(user)
        response = self.client.get(banner.get_absolute_url())
        self.assertEqual(response.status_code, 403)

    def test_preview_view_renders_banner(self):
        banner = Banner.objects.create(
            title="Draft banner",
            body="Some body text.",
            cta_label="Click here",
            cta_url="https://example.com/",
        )
        user = User.objects.create_user("previewer", "p@example.com", "password")
        user.user_permissions.add(Permission.objects.get(codename="view_banner"))
        self.client.force_login(user)
        response = self.client.get(banner.get_absolute_url())
        self.assertContains(response, "<h2>Draft banner</h2>", html=True)
        self.assertContains(response, "Some body text.")
        self.assertContains(
            response,
            '<a id="banner-cta" class="cta" href="https://example.com/">Click here</a>',
            html=True,
        )
        self.assertContains(response, "Preview!")

    def test_fundraising_page_suppresses_banner(self):
        Banner.objects.create(title="Donate now!", is_active=True)
        response = self.client.get("/fundraising/")
        self.assertNotContains(response, "Donate now!")
