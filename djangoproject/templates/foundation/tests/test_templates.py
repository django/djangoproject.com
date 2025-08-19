from django.test import TestCase
from foundation.models import Meeting, Business
from django.template import Context, Template

class LazyLoadingMeetingTemplateTests(TestCase):
    def test_meeting_body_html_has_lazy_loading(self):
        meeting = Meeting.objects.create(title="Test Meeting")
        business = Business.objects.create(title="Test Business", body_html='<p><img src="img.jpg"></p>')
        meeting.ongoing_business.add(business)

        template = Template("""
            {% load blog_extras %}
            {{ business.body_html|add_lazy_loading|safe }}
        """)
        rendered = template.render(Context({'business': business}))
        self.assertIn('loading="lazy"', rendered)
        self.assertIn('decoding="async"', rendered)
