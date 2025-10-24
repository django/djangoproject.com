import hashlib
from random import randint

from django.contrib.auth.models import AnonymousUser, User
from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings
from django_hosts.resolvers import reverse

from accounts.forms import DeleteProfileForm
from accounts.models import Profile
from foundation import models as foundationmodels
from tracdb.models import Revision, Ticket, TicketChange
from tracdb.testutils import TracDBCreateDatabaseMixin

from .forms import ProfileForm
from .views import edit_profile


@override_settings(TRAC_URL="https://code.djangoproject.com/")
class UserProfileTests(TracDBCreateDatabaseMixin, TestCase):
    databases = {"default", "trac"}

    @classmethod
    def setUpTestData(cls):
        user1_bio = "\n".join(
            [
                "[pre]",
                "\n",
                "Email: user1@example.com",
                "Website: user1.example.com",
                "GitHub: https://github.com/ghost",
                "\n",
                "[post]",
            ],
        )
        user2_bio = ""
        user1 = User.objects.create_user(username="user1", password="password")
        user2 = User.objects.create_user(username="user2", password="password")
        Profile.objects.create(user=user1, bio=user1_bio)
        Profile.objects.create(user=user2, bio=user2_bio)
        cls.user1_url = reverse("user_profile", args=["user1"])
        cls.user2_url = reverse("user_profile", args=["user2"])

    def test_username_is_page_title(self):
        response = self.client.get(self.user1_url)
        self.assertContains(response, '<h1 class="name">user1</h1>', html=True)

    def test_page_displays_bio_when_present(self):
        response = self.client.get(self.user1_url)
        self.assertContains(response, '<p class="bio">')

    def test_page_hides_bio_when_absent(self):
        response = self.client.get(self.user2_url)
        self.assertNotContains(response, '<p class="bio">')

    def test_bio_contains_mail_addresses_clickable(self):
        response = self.client.get(self.user1_url)
        self.assertContains(
            response,
            '<a href="mailto:user1@example.com">user1@example.com</a>',
            html=True,
        )

    def test_bio_contains_links_without_protocol_clickable(self):
        response = self.client.get(self.user1_url)
        self.assertContains(
            response,
            (
                '<a href="http://user1.example.com" rel="nofollow">'
                "user1.example.com</a>"
            ),
            html=True,
        )

    def test_bio_contains_links_with_protocol_clickable(self):
        response = self.client.get(self.user1_url)
        self.assertContains(
            response,
            (
                '<a href="https://github.com/ghost" rel="nofollow">'
                "https://github.com/ghost</a>"
            ),
            html=True,
        )

    def test_same_trac_username_can_be_used_for_multiple_users(self):
        # For the rare/temporal cases of when multiple accounts belong to
        # the same user.
        #
        # Please also see the comment in the function:
        # `tracdb.utils.check_if_public_trac_stats_are_renderable_for_user`

        self.assertFalse(Profile._meta.get_field("trac_username").unique)

    def test_stat_commits(self):
        Revision.objects.create(
            author="user1",
            rev="91c879eda595c12477bbfa6f51115e88b75ddf88",
            _time=1731669560,
        )
        Revision.objects.create(
            author="user1",
            rev="da2432cccae841f0d7629f17a5d79ec47ed7b7cb",
            _time=1731669560,
        )
        Revision.objects.create(
            author="user3",
            rev="63dbe30d3363715deaf280214d75b03f6d65a571",
            _time=1731669560,
        )

        user1_response = self.client.get(self.user1_url)
        user2_response = self.client.get(self.user2_url)
        self.assertContains(
            user1_response,
            '<a href="https://github.com/django/django/commits/main/'
            '?author=user1">Commits: 2.</a>',
            html=True,
        )
        self.assertNotContains(user2_response, "Commits")

    def test_stat_commits_for_custom_trac_username(self):
        djangoproject_username = "djangoproject_user"
        trac_username = "trac_user"
        user = User.objects.create_user(username=djangoproject_username)
        Profile.objects.create(user=user, trac_username=trac_username)

        Revision.objects.create(
            author=trac_username,
            rev="91c879eda595c12477bbfa6f51115e88b75ddf88",
            _time=1731669560,
        )
        Revision.objects.create(
            author=trac_username,
            rev="da2432cccae841f0d7629f17a5d79ec47ed7b7cb",
            _time=1731669560,
        )

        user_profile_url = reverse("user_profile", args=[djangoproject_username])
        user_profile_response = self.client.get(user_profile_url)
        self.assertContains(
            user_profile_response,
            '<a href="https://github.com/django/django/commits/main/'
            f'?author={trac_username}">Commits: 2.</a>',
            html=True,
        )

    def test_stat_commits_for_custom_trac_username_used_by_another_user(self):
        djangoproject_username1 = "djangoproject_user1"
        trac_username1 = "trac_user1"
        user1 = User.objects.create_user(username=djangoproject_username1)
        Profile.objects.create(user=user1, trac_username=trac_username1)

        djangoproject_username2 = trac_username1
        user2 = User.objects.create_user(username=djangoproject_username2)
        Profile.objects.create(user=user2)

        Revision.objects.create(
            author=trac_username1,
            rev="91c879eda595c12477bbfa6f51115e88b75ddf88",
            _time=1731669560,
        )
        Revision.objects.create(
            author=trac_username1,
            rev="da2432cccae841f0d7629f17a5d79ec47ed7b7cb",
            _time=1731669560,
        )

        user_profile_url2 = reverse("user_profile", args=[djangoproject_username2])
        user_profile_response2 = self.client.get(user_profile_url2)
        self.assertNotContains(user_profile_response2, "Commits")

    def test_stat_tickets(self):
        Ticket.objects.create(status="new", reporter="user1")
        Ticket.objects.create(status="new", reporter="user2")
        Ticket.objects.create(
            status="closed", reporter="user1", owner="user1", resolution="fixed"
        )
        Ticket.objects.create(
            status="closed", reporter="user2", owner="user1", resolution="fixed"
        )
        Ticket.objects.create(
            status="closed", reporter="user2", owner="user2", resolution="fixed"
        )
        Ticket.objects.create(
            status="closed", reporter="user2", owner="user1", resolution="wontfix"
        )

        user1_response = self.client.get(self.user1_url)
        user2_response = self.client.get(self.user2_url)
        self.assertContains(
            user1_response,
            '<a href="https://code.djangoproject.com/query?'
            'owner=user1&resolution=fixed&desc=1&order=changetime">'
            "Tickets fixed: 2.</a>",
            html=True,
        )
        self.assertContains(
            user2_response,
            '<a href="https://code.djangoproject.com/query?'
            'owner=user2&resolution=fixed&desc=1&order=changetime">'
            "Tickets fixed: 1.</a>",
            html=True,
        )
        self.assertContains(
            user1_response,
            '<a href="https://code.djangoproject.com/query?'
            'reporter=user1&desc=1&order=changetime">'
            "Tickets opened: 2.</a>",
            html=True,
        )
        self.assertContains(
            user2_response,
            '<a href="https://code.djangoproject.com/query?'
            'reporter=user2&desc=1&order=changetime">'
            "Tickets opened: 4.</a>",
            html=True,
        )

    def test_stat_tickets_for_custom_trac_username(self):
        djangoproject_username = "djangoproject_user"
        trac_username = "trac_user"
        user = User.objects.create_user(username=djangoproject_username)
        Profile.objects.create(user=user, trac_username=trac_username)

        Ticket.objects.create(status="new", reporter=trac_username)
        Ticket.objects.create(status="new", reporter="user2")
        Ticket.objects.create(
            status="closed",
            reporter=trac_username,
            owner=trac_username,
            resolution="fixed",
        )
        Ticket.objects.create(
            status="closed", reporter="user2", owner=trac_username, resolution="fixed"
        )
        Ticket.objects.create(
            status="closed", reporter="user2", owner="user2", resolution="fixed"
        )
        Ticket.objects.create(
            status="closed", reporter="user2", owner=trac_username, resolution="wontfix"
        )

        user_profile_url = reverse("user_profile", args=[djangoproject_username])
        user_profile_response = self.client.get(user_profile_url)
        self.assertContains(
            user_profile_response,
            '<a href="https://code.djangoproject.com/query?'
            f'owner={trac_username}&resolution=fixed&desc=1&order=changetime">'
            "Tickets fixed: 2.</a>",
            html=True,
        )
        self.assertContains(
            user_profile_response,
            '<a href="https://code.djangoproject.com/query?'
            f'reporter={trac_username}&desc=1&order=changetime">'
            "Tickets opened: 2.</a>",
            html=True,
        )

    def test_stat_tickets_for_custom_trac_username_used_by_another_user(self):
        djangoproject_username1 = "djangoproject_user1"
        trac_username1 = "trac_user1"
        user1 = User.objects.create_user(username=djangoproject_username1)
        Profile.objects.create(user=user1, trac_username=trac_username1)

        djangoproject_username2 = trac_username1
        user2 = User.objects.create_user(username=djangoproject_username2)
        Profile.objects.create(user=user2)

        Ticket.objects.create(status="new", reporter=trac_username1)
        Ticket.objects.create(status="new", reporter="user2")
        Ticket.objects.create(
            status="closed",
            reporter=trac_username1,
            owner=trac_username1,
            resolution="fixed",
        )
        Ticket.objects.create(
            status="closed", reporter="user2", owner=trac_username1, resolution="fixed"
        )
        Ticket.objects.create(
            status="closed", reporter="user2", owner="user2", resolution="fixed"
        )
        Ticket.objects.create(
            status="closed",
            reporter="user2",
            owner=trac_username1,
            resolution="wontfix",
        )

        user_profile_url2 = reverse("user_profile", args=[djangoproject_username2])
        user_profile_response2 = self.client.get(user_profile_url2)
        self.assertNotContains(user_profile_response2, "Tickets fixed:")

    def test_stat_tickets_triaged(self):
        # Possible values are from trac.ini in code.djangoproject.com.
        initial_ticket_values = {
            "field": "stage",
            "oldvalue": "Unreviewed",
            "_time": 1731669560,
        }
        TicketChange.objects.create(
            author="user1",
            newvalue="Accepted",
            ticket=Ticket.objects.create(),
            **initial_ticket_values,
        )
        TicketChange.objects.create(
            author="user1",
            newvalue="Someday/Maybe",
            ticket=Ticket.objects.create(),
            **initial_ticket_values,
        )
        TicketChange.objects.create(
            author="user1",
            newvalue="Ready for checkin",
            ticket=Ticket.objects.create(),
            **initial_ticket_values,
        )
        TicketChange.objects.create(
            author="user2",
            newvalue="Accepted",
            ticket=Ticket.objects.create(),
            **initial_ticket_values,
        )

        response = self.client.get(self.user1_url)
        self.assertContains(response, "New tickets triaged: 3.")

    def test_stat_tickets_triaged_for_custom_trac_username(self):
        djangoproject_username = "djangoproject_user"
        trac_username = "trac_user"
        user = User.objects.create_user(username=djangoproject_username)
        Profile.objects.create(user=user, trac_username=trac_username)

        # Possible values are from trac.ini in code.djangoproject.com.
        initial_ticket_values = {
            "field": "stage",
            "oldvalue": "Unreviewed",
            "_time": 1731669560,
        }
        TicketChange.objects.create(
            author=trac_username,
            newvalue="Accepted",
            ticket=Ticket.objects.create(),
            **initial_ticket_values,
        )
        TicketChange.objects.create(
            author=trac_username,
            newvalue="Someday/Maybe",
            ticket=Ticket.objects.create(),
            **initial_ticket_values,
        )
        TicketChange.objects.create(
            author=trac_username,
            newvalue="Ready for checkin",
            ticket=Ticket.objects.create(),
            **initial_ticket_values,
        )

        user_profile_url = reverse("user_profile", args=[djangoproject_username])
        user_profile_response = self.client.get(user_profile_url)
        self.assertContains(user_profile_response, "New tickets triaged: 3.")

    def test_stat_tickets_triaged_for_custom_trac_username_used_by_another_user(self):
        djangoproject_username1 = "djangoproject_user1"
        trac_username1 = "trac_user1"
        user1 = User.objects.create_user(username=djangoproject_username1)
        Profile.objects.create(user=user1, trac_username=trac_username1)

        djangoproject_username2 = trac_username1
        user2 = User.objects.create_user(username=djangoproject_username2)
        Profile.objects.create(user=user2)

        # Possible values are from trac.ini in code.djangoproject.com.
        initial_ticket_values = {
            "field": "stage",
            "oldvalue": "Unreviewed",
            "_time": 1731669560,
        }
        TicketChange.objects.create(
            author=trac_username1,
            newvalue="Accepted",
            ticket=Ticket.objects.create(),
            **initial_ticket_values,
        )
        TicketChange.objects.create(
            author=trac_username1,
            newvalue="Someday/Maybe",
            ticket=Ticket.objects.create(),
            **initial_ticket_values,
        )
        TicketChange.objects.create(
            author=trac_username1,
            newvalue="Ready for checkin",
            ticket=Ticket.objects.create(),
            **initial_ticket_values,
        )

        user_profile_url2 = reverse("user_profile", args=[djangoproject_username2])
        user_profile_response2 = self.client.get(user_profile_url2)
        self.assertNotContains(user_profile_response2, "New tickets triaged:")

    def test_stat_tickets_triaged_unaccepted_not_counted(self):
        common_ticket_values = {
            "field": "stage",
            "author": "user1",
            "_time": 1731669560,
        }
        TicketChange.objects.create(
            oldvalue="Unreviewed",
            newvalue="Accepted",
            ticket=Ticket.objects.create(),
            **common_ticket_values,
        )
        TicketChange.objects.create(
            oldvalue="Accepted",
            newvalue="Unreviewed",
            ticket=Ticket.objects.create(),
            **common_ticket_values,
        )

        response = self.client.get(self.user1_url)
        self.assertContains(response, "New tickets triaged: 1.")

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "unique-snowflake",
            }
        }
    )
    def test_caches_trac_stats(self):
        key = "trac_user_vital_status:%s" % hashlib.md5(b"user1").hexdigest()

        self.assertIsNone(cache.get(key))

        self.client.get(self.user1_url)

        self.assertIsNotNone(cache.get(key))


class UserProfileUpdateFormTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.edit_profile_url = reverse("edit_profile")

    def test_trac_username_field_is_excluded(self):
        form = ProfileForm()
        self.assertNotIn(
            "trac_username",
            form.fields,
            (
                "`ProfileForm` includes the field `trac_username`."
                " This may lead to security vulnerabilities."
            ),
        )

    def test_bio_field_has_max_length(self):
        form = ProfileForm()
        self.assertIsInstance(form.fields["bio"].max_length, int)

    def test_page_shows_characters_remaining_count_for_bio(self):
        profile_edit_form = ProfileForm()
        bio_field = profile_edit_form.fields["bio"]
        bio_length = randint(0, max(bio_field.max_length, 20))
        bio = "*" * bio_length
        expected_characters_remaining_count = bio_field.max_length - bio_length
        self.assertGreaterEqual(expected_characters_remaining_count, 0)
        user = User.objects.create_user(username="user", password="password")
        Profile.objects.create(user=user, bio=bio)
        request = self.request_factory.get(self.edit_profile_url)
        request.user = user
        response = edit_profile(request)
        self.assertContains(
            response,
            "<span>Characters remaining:</span>",
            html=True,
        )
        self.assertContains(
            response,
            f"""
                                class="character-counter__indicator"
                            >
                                {expected_characters_remaining_count}
                            </span>
            """.strip(),
        )


class ViewsTests(TestCase):

    def test_login_redirect(self):
        credentials = {"username": "a-user", "password": "password"}
        User.objects.create_user(**credentials)

        response = self.client.post(reverse("login"), credentials)
        self.assertRedirects(response, "/accounts/edit/")

    def test_profile_view_reversal(self):
        """
        The profile view can be reversed for usernames containing "weird" but
        valid username characters.
        """
        for username in ["asdf", "@asdf", "asd-f", "as.df", "as+df"]:
            reverse("user_profile", host="www", args=[username])


class UserDeletionTests(TestCase):
    def create_user_and_form(self, bound=True, **userkwargs):
        userkwargs.setdefault("username", "test")
        userkwargs.setdefault("email", "test@example.com")
        userkwargs.setdefault("password", "password")

        formkwargs = {"user": User.objects.create_user(**userkwargs)}
        if bound:
            formkwargs["data"] = {}

        return DeleteProfileForm(**formkwargs)

    def test_deletion(self):
        form = self.create_user_and_form()
        self.assertFormError(form, None, [])
        form.delete()
        self.assertQuerySetEqual(User.objects.all(), [])

    def test_anonymous_user_error(self):
        self.assertRaises(TypeError, DeleteProfileForm, user=AnonymousUser)

    def test_deletion_staff_forbidden(self):
        form = self.create_user_and_form(is_staff=True)
        self.assertFormError(form, None, ["Staff users cannot be deleted"])

    def test_user_with_protected_data(self):
        form = self.create_user_and_form()
        form.user.boardmember_set.create(
            office=foundationmodels.Office.objects.create(name="test"),
            term=foundationmodels.Term.objects.create(year=2000),
        )
        form.delete()
        self.assertFormError(
            form, None, ["User has protected data and cannot be deleted"]
        )

    def test_form_delete_method_requires_valid_form(self):
        form = self.create_user_and_form(is_staff=True)
        self.assertRaises(form.InvalidFormError, form.delete)

    def test_view_deletion_also_logs_out(self):
        user = self.create_user_and_form().user
        self.client.force_login(user)
        self.client.post(reverse("delete_profile"))
        self.assertEqual(self.client.cookies["sessionid"].value, "")
