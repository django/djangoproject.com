from urllib import parse as urlparse

from django.forms.models import modelform_factory
from django.test import TestCase
from django.utils import safestring
from django.utils.html import escape

from django_countries import countries, fields, widgets
from django_countries.conf import settings
from django_countries.tests.models import Person


def person_form(widgets={"country": widgets.CountrySelectWidget}, **kwargs):
    return modelform_factory(Person, fields=["country"], widgets=widgets, **kwargs)


class TestCountrySelectWidget(TestCase):
    def setUp(self):
        del countries.countries

    def tearDown(self):
        del countries.countries

    def test_not_default_widget(self):
        PersonForm = person_form(widgets={})
        widget = PersonForm().fields["country"].widget
        self.assertFalse(isinstance(widget, widgets.CountrySelectWidget))

    def test_render_contains_flag_url(self):
        with self.settings(COUNTRIES_ONLY={"AU": "Desert"}):
            PersonForm = person_form()
            html = PersonForm().as_p()
            self.assertIn(
                escape(
                    urlparse.urljoin(settings.STATIC_URL, settings.COUNTRIES_FLAG_URL)
                ),
                html,
            )

    def test_render(self):
        with self.settings(COUNTRIES_ONLY={"AU": "Desert"}):
            PersonForm = person_form()
            html = PersonForm().as_p()
            self.assertInHTML("""<option value="AU">Desert</option>""", html, count=1)
            self.assertIn(fields.Country("__").flag, html)
            self.assertNotIn(fields.Country("AU").flag, html)

    def test_render_initial(self):
        with self.settings(COUNTRIES_ONLY={"AU": "Desert"}):
            PersonForm = person_form()
            html = PersonForm(initial={"country": "AU"}).as_p()
            self.assertIn(fields.Country("AU").flag, html)
            self.assertNotIn(fields.Country("__").flag, html)

    def test_render_escaping(self):
        output = widgets.CountrySelectWidget().render("test", "<script>")
        self.assertIn("&lt;script&gt;", output)
        self.assertNotIn("<script>", output)
        self.assertTrue(isinstance(output, safestring.SafeData))

    def test_render_modelform_instance(self):
        person = Person(country="NZ")
        PersonForm = person_form()
        PersonForm(instance=person).as_p()

    def test_required_attribute(self):
        PersonForm = person_form()
        rendered = PersonForm()["country"].as_widget()
        rendered = rendered[: rendered.find(">") + 1]
        self.assertIn("required", rendered)
