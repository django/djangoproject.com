from django.contrib.auth.models import User
from django.test import TestCase

class MeetingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(
            "admin", "admin@example.com", "password"
        )

    def test_latest_meeting_minutes(self):
        pass

        # TODO: Find a way to initalize the foundation page without using the Meeting
        # object

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
