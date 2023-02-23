from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import BoardMember, Meeting, Office, Term


class MeetingTestCase(TestCase):
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
            title="Minutes",
            slug="minutes",
            leader=member,
            treasurer_report="Hello World",
        )

        response = self.client.get(reverse("foundation-minutes-feed"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hello World", response.content)
