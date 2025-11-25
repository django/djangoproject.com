import pickle
import tempfile
from unittest import mock
from unittest.case import skipUnless

import django
import pytest
from django.core import checks, validators
from django.core.management import call_command
from django.db import models
from django.forms import Select
from django.forms.models import modelform_factory
from django.test import TestCase, override_settings
from django.utils import translation
from django.utils.encoding import force_str

from django_countries import countries, data, fields
from django_countries.conf import settings
from django_countries.fields import CountryField
from django_countries.tests import custom_countries, forms
from django_countries.tests.models import AllowNull, MultiCountry, Person, WithProp


# Django 3.2 introduced a db_collation attr on fields.
def has_db_collation() -> bool:
    major, minor = django.VERSION[0:2]
    return (major > 3) or (major == 3 and minor >= 2)


class TestCountryField(TestCase):
    @skipUnless(has_db_collation(), "Django version < 3.2")
    def test_db_collation(self):
        # test fix for issue 338
        country = fields.CountryField()
        self.assertTrue(hasattr(country, "db_collation"))

    def test_logic(self):
        person = Person(name="Chris Beaven", country="NZ")

        self.assertEqual(person.country, "NZ")
        self.assertNotEqual(person.country, "ZZ")

        self.assertTrue(person.country)
        person.country = ""
        self.assertFalse(person.country)

    def test_get_property_from_class(self):
        self.assertIsInstance(Person.country, fields.CountryDescriptor)

    def test_deconstruct(self):
        field = Person._meta.get_field("country")
        self.assertEqual(
            field.deconstruct(),
            ("country", "django_countries.fields.CountryField", [], {"max_length": 2}),
        )

    def test_text(self):
        person = Person(name="Chris Beaven", country="NZ")
        self.assertEqual(force_str(person.country), "NZ")

    def test_name(self):
        person = Person(name="Chris Beaven", country="NZ")
        self.assertEqual(person.country.name, "New Zealand")

    def test_flag(self):
        person = Person(name="Chris Beaven", country="NZ")
        with self.settings(STATIC_URL="/static-assets/"):
            self.assertEqual(person.country.flag, "/static-assets/flags/nz.gif")

    def test_custom_field_flag_url(self):
        person = Person(name="Chris Beaven", country="NZ", other_country="US")
        self.assertEqual(person.other_country.flag, "//flags.example.com/us.gif")

    def test_custom_field_str_attr(self):
        person = Person(name="Quentin Coumes", country="FR", str_attr_country="ES")
        self.assertEqual(str(person.str_attr_country), "Spain")

    def test_unicode_flags(self):
        person = Person(name="Matthew Schinckel", country="AU", other_country="DE")
        self.assertEqual(person.country.unicode_flag, "🇦🇺")
        self.assertEqual(person.other_country.unicode_flag, "🇩🇪")

    def test_unicode_flag_blank(self):
        person = Person(name="Matthew Schinckel")
        self.assertEqual(person.country.unicode_flag, "")

    def test_COUNTRIES_FLAG_URL_setting(self):
        # Custom relative url
        person = Person(name="Chris Beaven", country="NZ")
        with self.settings(
            COUNTRIES_FLAG_URL="img/flag-{code_upper}.png", STATIC_URL="/static-assets/"
        ):
            self.assertEqual(person.country.flag, "/static-assets/img/flag-NZ.png")
        # Custom absolute url
        with self.settings(
            COUNTRIES_FLAG_URL="https://flags.example.com/{code_upper}.PNG"
        ):
            self.assertEqual(person.country.flag, "https://flags.example.com/NZ.PNG")

    def test_flag_css(self):
        person = Person(name="Chris Beaven", country="NZ")
        self.assertEqual(person.country.flag_css, "flag-sprite flag-n flag-_z")

    def test_flag_css_blank(self):
        person = Person(name="Chris Beaven")
        self.assertEqual(person.country.flag_css, "")

    def test_blank(self):
        person = Person.objects.create(name="The Outsider")
        self.assertEqual(person.country.code, "")

        person = Person.objects.get(pk=person.pk)
        self.assertEqual(person.country.code, "")

    def test_null(self):
        person = AllowNull.objects.create(country=None)
        self.assertIsNone(person.country.code)

        person = AllowNull.objects.get(pk=person.pk)
        self.assertIsNone(person.country.code)

    @override_settings(SILENCED_SYSTEM_CHECKS=["django_countries.E100"])
    def test_multi_null_country(self):
        try:

            class MultiNullCountry(models.Model):
                countries = fields.CountryField(multiple=True, null=True, blank=True)

            class MultiNullCountryNoBlank(models.Model):
                countries = fields.CountryField(multiple=True, null=True)

            errors = checks.run_checks()
            self.assertEqual([e.id for e in errors], ["django_countries.E100"] * 2)
            errors_dict = {e.obj: e for e in errors}
            self.assertFalse(
                "blank=True"
                in errors_dict[MultiNullCountry._meta.get_field("countries")].hint
            )
            self.assertTrue(
                "blank=True"
                in errors_dict[
                    MultiNullCountryNoBlank._meta.get_field("countries")
                ].hint
            )
        finally:
            from django.apps import apps

            test_config = apps.get_app_config("django_countries_tests")
            test_config.models.pop("multinullcountry")
            test_config.models.pop("multinullcountrynoblank")

    def test_deferred(self):
        Person.objects.create(name="Person", country="NZ")
        person = Person.objects.defer("country").get(name="Person")
        self.assertEqual(person.country.code, "NZ")

    def test_only(self):
        Person.objects.create(name="Person", country="NZ")
        person = Person.objects.only("name").get()
        self.assertEqual(person.country.code, "NZ")

    def test_nullable_deferred(self):
        AllowNull.objects.create(country=None)
        person = AllowNull.objects.defer("country").get()
        self.assertIsNone(person.country.code)

    def test_len(self):
        person = Person(name="Chris Beaven", country="NZ")
        self.assertEqual(len(person.country), 2)

        person = Person(name="The Outsider", country=None)
        self.assertEqual(len(person.country), 0)

    def test_lookup_text(self):
        Person.objects.create(name="Chris Beaven", country="NZ")
        Person.objects.create(name="Pavlova", country="NZ")
        Person.objects.create(name="Killer everything", country="AU")

        lookup = Person.objects.filter(country="NZ")
        names = lookup.order_by("name").values_list("name", flat=True)
        self.assertEqual(list(names), ["Chris Beaven", "Pavlova"])

    def test_lookup_country(self):
        Person.objects.create(name="Chris Beaven", country="NZ")
        Person.objects.create(name="Pavlova", country="NZ")
        Person.objects.create(name="Killer everything", country="AU")

        oz = fields.Country(code="AU", flag_url="")
        lookup = Person.objects.filter(country=oz)
        names = lookup.values_list("name", flat=True)
        self.assertEqual(list(names), ["Killer everything"])

    def test_save_empty_country(self):
        Person.objects.create(name="The Outsider")
        person = Person.objects.get()
        self.assertEqual(person.country.code, "")

    def test_create_modelform(self):
        Form = modelform_factory(Person, fields=["country"])
        form_field = Form().fields["country"]
        self.assertTrue(isinstance(form_field.widget, Select))

    def test_render_form(self):
        Form = modelform_factory(Person, fields=["country"])
        Form().as_p()

    def test_model_with_prop(self):
        with_prop = WithProp(country="FR", public_field="test")

        self.assertEqual(with_prop.country.code, "FR")
        self.assertEqual(with_prop.public_field, "test")

    def test_in(self):
        Person.objects.create(name="A", country="NZ")
        Person.objects.create(name="B", country="AU")
        Person.objects.create(name="C", country="FR")
        Person.objects.create(name="D", country="NZ")

        self.assertEqual(
            list(
                Person.objects.filter(country__in=["AU", "NZ"]).values_list(
                    "name", flat=True
                )
            ),
            ["A", "B", "D"],
        )

    def test_exact(self):
        p = Person.objects.create(name="A", country="NZ")
        self.assertEqual(list(Person.objects.filter(country__exact="NZ")), [p])
        self.assertEqual(list(Person.objects.filter(country__exact="nz")), [])
        self.assertEqual(list(Person.objects.filter(country__exact="New Zealand")), [])

    def test_iexact(self):
        p = Person.objects.create(name="A", country="NZ")
        self.assertEqual(list(Person.objects.filter(country__iexact="nz")), [p])

    def test_by_country_name(self):
        p = Person.objects.create(name="A", country="NZ")
        self.assertEqual(list(Person.objects.filter(country__name="New Zealand")), [p])
        self.assertEqual(list(Person.objects.filter(country__name="new zealand")), [])
        self.assertEqual(list(Person.objects.filter(country__iname="new zealand")), [p])
        self.assertEqual(list(Person.objects.filter(country__iname="new z")), [])

    def test_by_country_name_contains(self):
        p = Person.objects.create(name="A", country="NZ")
        pp = Person.objects.create(name="A", country="NC")
        self.assertEqual(list(Person.objects.filter(country__contains="ew")), [p, pp])
        self.assertEqual(list(Person.objects.filter(country__contains="EW")), [])
        self.assertEqual(list(Person.objects.filter(country__icontains="EW")), [p, pp])
        # Also works with country codes.
        self.assertEqual(list(Person.objects.filter(country__contains="NZ")), [p])
        self.assertEqual(list(Person.objects.filter(country__contains="nz")), [])
        self.assertEqual(list(Person.objects.filter(country__icontains="nz")), [p])

    def test_by_country_name_startswith(self):
        p = Person.objects.create(name="A", country="ZA")  # South Africa
        pp = Person.objects.create(
            name="A", country="TF"
        )  # French Southern Territories
        self.assertEqual(set(Person.objects.filter(country__contains="South")), {p, pp})
        self.assertEqual(list(Person.objects.filter(country__startswith="South")), [p])
        self.assertEqual(list(Person.objects.filter(country__startswith="south")), [])
        self.assertEqual(list(Person.objects.filter(country__istartswith="south")), [p])
        # Also works with country codes.
        self.assertEqual(list(Person.objects.filter(country__startswith="ZA")), [p])
        self.assertEqual(list(Person.objects.filter(country__startswith="za")), [])
        self.assertEqual(list(Person.objects.filter(country__istartswith="za")), [p])

    def test_by_country_name_endswith(self):
        p = Person.objects.create(name="A", country="AS")  # American Samoa
        pp = Person.objects.create(name="A", country="US")  # United States of America
        self.assertEqual(
            set(Person.objects.filter(country__contains="America")), {p, pp}
        )
        self.assertEqual(list(Person.objects.filter(country__endswith="America")), [pp])
        self.assertEqual(list(Person.objects.filter(country__endswith="america")), [])
        self.assertEqual(
            list(Person.objects.filter(country__iendswith="america")), [pp]
        )
        # Also works with country codes.
        self.assertEqual(list(Person.objects.filter(country__endswith="US")), [pp])
        self.assertEqual(list(Person.objects.filter(country__endswith="us")), [])
        self.assertEqual(list(Person.objects.filter(country__iendswith="us")), [pp])

    def test_by_country_name_regex(self):
        p = Person.objects.create(name="A", country="MK")  # North Macedonia
        pp = Person.objects.create(name="A", country="MP")  # Northern Mariana Islands
        self.assertEqual(set(Person.objects.filter(country__contains="North")), {p, pp})
        self.assertEqual(list(Person.objects.filter(country__regex=r"North\b")), [p])
        self.assertEqual(list(Person.objects.filter(country__regex=r"north\b")), [])
        self.assertEqual(list(Person.objects.filter(country__iregex=r"north\b")), [p])
        # Also works with country codes.
        self.assertEqual(list(Person.objects.filter(country__regex="MP")), [pp])
        self.assertEqual(list(Person.objects.filter(country__regex="mp")), [])
        self.assertEqual(list(Person.objects.filter(country__iregex="mp")), [pp])


class TestValidation(TestCase):
    def test_validate(self):
        person = Person(name="Chris", country="NZ")
        person.full_clean()

    def test_validate_alpha3(self):
        person = Person(name="Chris", country="NZL")
        person.full_clean()

    def test_validate_empty(self):
        person = Person(name="Chris")
        self.assertRaises(validators.ValidationError, person.full_clean)

    def test_validate_invalid(self):
        person = Person(name="Chris", country=":(")
        self.assertRaises(validators.ValidationError, person.full_clean)

    def test_validate_multiple(self):
        person = MultiCountry(countries=["NZ", "AU"])
        person.full_clean()

    def test_validate_multiple_empty(self):
        person = MultiCountry()
        self.assertRaises(validators.ValidationError, person.full_clean)

    def test_validate_multiple_invalid(self):
        person = MultiCountry(countries=[":(", "AU"])
        self.assertRaises(validators.ValidationError, person.full_clean)

    def test_validate_multiple_uneditable(self):
        person = MultiCountry(countries="NZ", uneditable_countries="xx")
        person.full_clean()

    def test_get_prep_value_empty_string(self):
        country_field_instance = CountryField(multiple=True, blank=True)
        prep_value = country_field_instance.get_prep_value("")
        self.assertEqual(prep_value, "")

    def test_get_prep_value_none(self):
        """
        Note: django migrations will call get_prep_value() with None
        see: https://github.com/SmileyChris/django-countries/issues/215
        """
        country_field_instance = CountryField(multiple=True, blank=True)
        prep_value = country_field_instance.get_prep_value(None)
        self.assertEqual(prep_value, "")

    def test_get_prep_value_invalid_type(self):
        country_field_instance = CountryField(multiple=True, blank=True)
        prep_value = country_field_instance.get_prep_value(0)
        self.assertEqual(prep_value, "0")


class TestCountryCustom(TestCase):
    def test_name(self):
        person = Person(name="Chris Beaven", fantasy_country="NV")
        self.assertEqual(person.fantasy_country.name, "Neverland")

    def test_field(self):
        self.assertEqual(
            list(Person._meta.get_field("fantasy_country").choices),
            [("NV", "Neverland"), ("NZ", "New Zealand")],
        )

    def test_deconstruct(self):
        field = Person._meta.get_field("fantasy_country")
        self.assertEqual(
            field.deconstruct(),
            (
                "fantasy_country",
                "django_countries.fields.CountryField",
                [],
                {
                    "countries": custom_countries.FantasyCountries,
                    "blank": True,
                    "max_length": 2,
                },
            ),
        )


def test_longer_country_code_deconstruction():
    field = CountryField(countries=custom_countries.GBRegionCountries)
    assert field.deconstruct() == (
        None,
        "django_countries.fields.CountryField",
        [],
        {"countries": custom_countries.GBRegionCountries, "max_length": 6},
    )


def test_longer_country_code_multiple_deconstruction():
    field = CountryField(countries=custom_countries.GBRegionCountries, multiple=True)
    expected_max_length = (
        # Commas
        (len(field.countries) - 1)
        # Country codes
        + sum(len(code) for code in field.countries.countries)
    )
    assert field.deconstruct() == (
        None,
        "django_countries.fields.CountryField",
        [],
        {
            "countries": custom_countries.GBRegionCountries,
            "max_length": expected_max_length,
            "multiple": True,
        },
    )


class TestCountryMultiple(TestCase):
    def test_empty(self):
        obj = MultiCountry()
        self.assertEqual(obj.countries, [])

    def test_empty_save(self):
        MultiCountry.objects.create()

    def test_single(self):
        obj = MultiCountry(countries="NZ")
        self.assertEqual(len(obj.countries), 1)
        self.assertTrue(isinstance(obj.countries[0], fields.Country))
        self.assertEqual(obj.countries[0], "NZ")

    def test_multiple(self):
        obj = MultiCountry(countries="AU,NZ")
        self.assertEqual(len(obj.countries), 2)
        for country in obj.countries:
            self.assertTrue(isinstance(country, fields.Country))
        self.assertEqual(obj.countries[0], "AU")
        self.assertEqual(obj.countries[1], "NZ")

    def test_multiple_with_duplicates(self):
        codes = "NZ,AU,NZ"
        obj = MultiCountry(
            countries=codes,
            unsorted_countries=codes,
            duplicate_countries=codes,
            unsorted_duplicate_countries=codes,
        )
        for country in obj.countries:
            self.assertTrue(isinstance(country, fields.Country))
        self.assertEqual(obj.countries, ["AU", "NZ"])
        self.assertEqual(obj.unsorted_countries, ["NZ", "AU"])
        self.assertEqual(obj.duplicate_countries, ["AU", "NZ", "NZ"])
        self.assertEqual(obj.unsorted_duplicate_countries, ["NZ", "AU", "NZ"])

        obj = MultiCountry(countries="")
        self.assertEqual(obj.countries, [])

    def test_set_text(self):
        obj = MultiCountry()
        obj.countries = "NZ,AU"
        self.assertEqual(obj.countries, ["AU", "NZ"])

    def test_set_list(self):
        obj = MultiCountry()
        obj.countries = ["NZ", "AU"]
        self.assertEqual(obj.countries, ["AU", "NZ"])

    def test_set_country(self):
        obj = MultiCountry()
        obj.countries = fields.Country("NZ")
        self.assertEqual(obj.countries, ["NZ"])

    def test_set_countries(self):
        obj = MultiCountry()
        obj.countries = [fields.Country("NZ"), fields.Country("AU")]
        self.assertEqual(obj.countries, ["AU", "NZ"])

    def test_all_countries(self):
        all_codes = sorted(c[0] for c in countries)
        MultiCountry.objects.create(countries=all_codes)
        obj = MultiCountry.objects.get()
        self.assertEqual(obj.countries, all_codes)

    def test_deconstruct(self):
        field = MultiCountry._meta.get_field("countries")
        expected_max_length = len(data.COUNTRIES) * 3 - 1
        self.assertEqual(
            field.deconstruct(),
            (
                "countries",
                "django_countries.fields.CountryField",
                [],
                {"max_length": expected_max_length, "multiple": True},
            ),
        )

    def test_contains(self):
        obj = MultiCountry.objects.create(countries=["NZ", "AU"])
        qs = MultiCountry.objects.filter(countries__contains="NZ")
        self.assertEqual(list(qs), [obj])


class TestCountryObject(TestCase):
    def test_hash(self):
        country = fields.Country(code="XX", flag_url="")
        self.assertEqual(hash(country), hash("XX"))

    def test_repr(self):
        country1 = fields.Country(code="XX")
        country2 = fields.Country(code="XX", flag_url="")
        country3 = fields.Country(code="XX", str_attr="name")
        self.assertEqual(repr(country1), f"Country(code={'XX'!r})")
        self.assertEqual(
            repr(country2),
            f"Country(code={'XX'!r}, flag_url={''!r})",
        )
        self.assertEqual(
            repr(country3),
            f"Country(code={'XX'!r}, str_attr={'name'!r})",
        )

    def test_str(self):
        country = fields.Country(code="NZ")
        self.assertEqual(str(country), "NZ")

    def test_str_attr(self):
        country = fields.Country(code="NZ", str_attr="name")
        self.assertEqual(str(country), "New Zealand")

    def test_flag_on_empty_code(self):
        country = fields.Country(code="", flag_url="")
        self.assertEqual(country.flag, "")

    def test_ioc_code(self):
        country = fields.Country(code="NL", flag_url="")
        self.assertEqual(country.ioc_code, "NED")

    def test_country_from_ioc_code(self):
        country = fields.Country.country_from_ioc("NED")
        self.assertEqual(country, fields.Country("NL", flag_url=""))

    def test_country_from_blank_ioc_code(self):
        country = fields.Country.country_from_ioc("")
        self.assertIsNone(country)

    def test_country_from_nonexistence_ioc_code(self):
        country = fields.Country.country_from_ioc("XXX")
        self.assertIsNone(country)

    def test_alpha3(self):
        country = fields.Country(code="BN")
        self.assertEqual(country.alpha3, "BRN")

    def test_alpha3_invalid(self):
        country = fields.Country(code="XX")
        self.assertEqual(country.alpha3, "")

    def test_numeric(self):
        country = fields.Country(code="BN")
        self.assertEqual(country.numeric, 96)

    def test_numeric_padded(self):
        country = fields.Country(code="AL")
        self.assertEqual(country.numeric_padded, "008")
        country = fields.Country(code="BN")
        self.assertEqual(country.numeric_padded, "096")
        country = fields.Country(code="NZ")
        self.assertEqual(country.numeric_padded, "554")

    def test_numeric_invalid(self):
        country = fields.Country(code="XX")
        self.assertEqual(country.numeric, None)

    def test_numeric_padded_invalid(self):
        country = fields.Country(code="XX")
        self.assertEqual(country.numeric_padded, None)

    def test_empty_flag_url(self):
        country = fields.Country(code="XX", flag_url="")
        self.assertEqual(country.flag, "")

    def test_alpha2_code(self):
        country = fields.Country(code="NZL")
        self.assertEqual(country.code, "NZ")

    def test_alpha2_code_invalid(self):
        country = fields.Country(code="NZX")
        self.assertEqual(country.code, "NZX")

    def test_numeric_code(self):
        country = fields.Country(code=554)
        self.assertEqual(country.code, "NZ")

    def test_numeric_code_invalid(self):
        country = fields.Country(code=999)
        self.assertEqual(country.code, 999)

    def test_extensions(self):
        with mock.patch.object(fields, "EXTENSIONS", {"codex2": lambda c: c.code * 2}):
            country = fields.Country(code="NZ")
            self.assertEqual(country.codex2, "NZNZ")


class TestModelForm(TestCase):
    @pytest.mark.skipif(not settings.USE_I18N, reason="No i18n")
    def test_translated_choices(self):
        lang = translation.get_language()
        translation.activate("eo")
        form = forms.PersonForm()
        try:
            # This is just to prove that the language changed.
            self.assertEqual(list(countries)[0][1], "Afganio")
            # If the choices aren't lazy, this wouldn't be translated. It's the
            # second choice because the first one is the initial blank option.
            self.assertEqual(form.fields["country"].choices[1][1], "Afganio")
            self.assertEqual(form.fields["country"].widget.choices[1][1], "Afganio")
        finally:
            translation.activate(lang)

    def test_blank_choice(self):
        blank = ("", "---------")

        form = forms.PersonForm()
        self.assertEqual(form.fields["country"].choices[0], blank)
        html = str(form["country"]).split(">", 1)[0]
        self.assertEqual(html, '<select name="country" required id="id_country"')

        multi_form = forms.MultiCountryForm()
        self.assertNotEqual(multi_form.fields["countries"].choices[0], blank)
        html = str(multi_form["countries"]).split(">", 1)[0]
        expected = '<select name="countries" required id="id_countries" multiple'
        self.assertEqual(html, expected)

    def test_no_blank_choice(self):
        form = forms.PersonForm()
        self.assertEqual(
            form.fields["favourite_country"].choices[0], ("AF", "Afghanistan")
        )

    def test_blank_choice_label(self):
        form = forms.AllowNullForm()
        self.assertEqual(form.fields["country"].choices[0], ("", "(select country)"))
        html = str(form["country"]).split(">", 1)[0]
        self.assertEqual(html, '<select name="country" id="id_country"')

    def test_validation(self):
        form = forms.MultiCountryForm(data={"countries": ["NZ", "AU"]})
        self.assertEqual(form.errors, {})


class TestPickling(TestCase):
    def test_standard_country_pickling(self):
        chris = Person(name="Chris Beaven", country="NZ")
        # django uses pickle.HIGHEST_PROTOCOL which is somewhere between 2 and
        # 4, depending on python version. Let's use 2 for testing.
        newly_pickled_zealand = pickle.dumps(chris.country, protocol=2)
        # Different python versions end up with slightly different sizes. Let's
        # just check the size is smaller than if it contained the entire
        # standard countries list in the pickle.
        self.assertLess(len(newly_pickled_zealand), 200)

        unpickled = pickle.loads(newly_pickled_zealand)
        self.assertEqual(unpickled.code, "NZ")
        self.assertEqual(unpickled.name, "New Zealand")
        self.assertEqual(unpickled.flag_url, None)
        self.assertIs(unpickled.countries, countries)
        self.assertIsNone(unpickled.custom_countries)

    def test_custom_country_pickling(self):
        chris = Person(name="Chris Beaven", fantasy_country="NV")
        # django uses pickle.HIGHEST_PROTOCOL which is somewhere between 2 and
        # 4, depending on python version. Let's use 2 for testing.
        pickled_neverland = pickle.dumps(chris.fantasy_country, protocol=2)
        # Different python versions end up with slightly different sizes. Let's
        # just check the size is smaller than if it also contained the fantasy
        # countries list in the pickle.
        self.assertLess(len(pickled_neverland), 300)

        neverland = pickle.loads(pickled_neverland)
        self.assertEqual(neverland.code, "NV")
        self.assertEqual(neverland.name, "Neverland")
        self.assertEqual(neverland.flag_url, None)
        self.assertIsInstance(neverland.countries, custom_countries.FantasyCountries)


class TestLoadData(TestCase):
    def test_basic(self):
        single = Person.objects.create(name="Chris Beaven", country="NZ")
        multi = MultiCountry.objects.create(countries=["NZ", "AU"])
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w+") as capture:
            call_command("dumpdata", "django_countries_tests", stdout=capture)
            single.delete()
            multi.delete()
            capture.flush()
            capture.seek(0)
            call_command("loaddata", capture.name, "-v", "0")
        self.assertEqual(Person.objects.get().country, "NZ")
        countries = MultiCountry.objects.get().countries
        countries = [country.code for country in countries]
        self.assertEqual(countries, ["AU", "NZ"])
