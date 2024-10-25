from datetime import datetime, time

from django.contrib.syndication.views import Feed
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _

from .models import Meeting


class FoundationMinutesFeed(Feed):
    title = _("The DSF meeting minutes")
    link = "https://www.djangoproject.com/foundation/minutes/"
    description = _("The meeting minutes of the Django Software Foundation's board.")

    def items(self):
        return Meeting.objects.order_by("-date")[:10]

    def item_pubdate(self, item):
        return make_aware(datetime.combine(item.date, time.min))

    def item_author_name(self, item):
        return _("DSF Board")

    def item_title(self, item):
        return str(item)
