from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import BoardMember, Meeting, Office, Term


class MeetingTestCase(TestCase):
    def test_meeting_initial(self):
        user = User.objects.create_superuser("admin", "admin@example.com", "password")
        self.client.force_login(user)
        response = self.client.get(reverse("admin:foundation_meeting_add"))
        self.assertContains(response, "DSF Board monthly meeting")
        self.assertContains(response, "dsf-board-monthly-meeting")

    def test_meeting_minutes_feed(self):
        """
        Make sure that the meeting minutes RSS feed works
        """
        user = User.objects.create_superuser("admin", "admin@example.com", "password")
        member = BoardMember.objects.create(
            account=user,
            office=Office.objects.create(name="treasurer"),
            term=Term.objects.create(year=2023),
        )
        Meeting.objects.create(
            date=date.today(),
            title="DSF Board monthly meeting",
            slug="dsf-board-monthly-meeting",
            leader=member,
            treasurer_report="Hello World",
        )

        response = self.client.get(reverse("foundation-minutes-feed"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"DSF Board monthly meeting", response.content)
