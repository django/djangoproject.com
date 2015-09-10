from datetime import timedelta
from django.utils import timezone


class DateTimeMixin(object):
    def setUp(self):
        self.now = timezone.now()
        self.yesterday = self.now - timedelta(days=1)
        self.tomorrow = self.now + timedelta(days=1)
