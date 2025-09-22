from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from djmoney.money import Money

from djangoproject.tests import ReleaseMixin

from .models import ApprovedGrant, BoardMember, Business, Meeting, Office, Term


class MeetingTestCase(ReleaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_superuser(
            "admin", "admin@example.com", "password"
        )
        cls.member = BoardMember.objects.create(
            account=cls.user,
            office=Office.objects.create(name="treasurer"),
            term=Term.objects.create(year=2023),
        )

    def test_meeting_initial(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin:foundation_meeting_add"))
        self.assertContains(response, "DSF Board monthly meeting")
        self.assertContains(response, "dsf-board-monthly-meeting")

    def test_meeting_minutes_feed(self):
        """
        Make sure that the meeting minutes RSS feed works
        """
        Meeting.objects.create(
            date=date.today(),
            title="DSF Board monthly meeting",
            slug="dsf-board-monthly-meeting",
            leader=self.member,
            treasurer_report="Hello World",
        )

        response = self.client.get(reverse("foundation-minutes-feed"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"DSF Board monthly meeting", response.content)

    def test_meeting_details(self):
        meeting = Meeting.objects.create(
            date=date(2023, 1, 12),
            title="DSF Board monthly meeting",
            slug="dsf-board-monthly-meeting",
            leader=self.member,
            treasurer_report="Hello World",
        )
        ApprovedGrant.objects.create(
            entity="Django girls",
            amount=Money("10000", "USD"),
            approved_at=meeting,
        )
        ApprovedGrant.objects.create(
            entity="DjangoCon EU",
            amount=Money(5000, "EUR"),
            approved_at=meeting,
        )
        response = self.client.get(
            reverse(
                "foundation_meeting_detail",
                kwargs={
                    "year": 2023,
                    "month": "jan",
                    "day": 12,
                    "slug": "dsf-board-monthly-meeting",
                },
            )
        )
        self.assertContains(response, "DSF Board monthly meeting")
        self.assertContains(response, "USD $10,000.00")
        self.assertContains(response, "EUR €5,000.00")

    def test_latest_meeting_minutes(self):
        common_meeting_data = {
            "slug": "dsf-board-monthly-meeting",
            "leader": self.member,
            "treasurer_report": "Hello World",
            "title": "DSF Board monthly meeting",
        }
        Meeting.objects.create(date=date(2023, 3, 12), **common_meeting_data)
        response = self.client.get(reverse("foundation_meeting_archive_index"))

        self.assertContains(response, "Latest DSF meeting minutes")
        self.assertContains(response, "https://github.com/django/dsf-minutes")
