import pytest
from django.test import TestCase, override_settings
from rest_framework import serializers, views
from rest_framework.test import APIRequestFactory

from django_countries import countries
from django_countries.conf import settings
from django_countries.fields import Country
from django_countries.serializers import CountryFieldMixin
from django_countries.tests.custom_countries import FantasyCountries
from django_countries.tests.models import MultiCountry, Person


def countries_display(countries):
    """
    Convert Countries into a DRF-OPTIONS formatted dict.
    """
    return [{"display_name": v, "value": k} for (k, v) in countries]


class PersonSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = (
            "name",
            "country",
            "other_country",
            "favourite_country",
            "fantasy_country",
        )
        extra_kwargs = {
            "other_country": {"country_dict": True},
            "favourite_country": {"name_only": True},
        }


class MultiCountrySerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = MultiCountry
        fields = ("countries",)


class TestDRF(TestCase):
    def test_serialize(self):
        person = Person(name="Chris Beaven", country="NZ")
        serializer = PersonSerializer(person)
        self.assertEqual(
            serializer.data,
            {
                "name": "Chris Beaven",
                "country": "NZ",
                "other_country": "",
                "favourite_country": "New Zealand",
                "fantasy_country": "",
            },
        )

    def test_serialize_country_dict(self):
        person = Person(name="Chris Beaven", other_country="AU")
        serializer = PersonSerializer(person)
        self.assertEqual(
            serializer.data,
            {
                "name": "Chris Beaven",
                "country": "",
                "other_country": {"code": "AU", "name": "Australia"},
                "favourite_country": "New Zealand",
                "fantasy_country": "",
            },
        )

    def test_deserialize(self):
        serializer = PersonSerializer(
            data={"name": "Tester", "country": "US", "fantasy_country": "NV"}
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["country"], "US")

    def test_deserialize_country_dict(self):
        serializer = PersonSerializer(
            data={
                "name": "Tester",
                "country": {"code": "GB", "name": "Anything"},
                "fantasy_country": "NV",
            }
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["country"], "GB")

    def test_deserialize_by_name(self):
        serializer = PersonSerializer(
            data={
                "name": "Chris",
                "country": "New Zealand",
                "fantasy_country": "Neverland",
            }
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["country"], "NZ")
        self.assertEqual(serializer.validated_data["fantasy_country"], "NV")

    def test_deserialize_invalid(self):
        serializer = PersonSerializer(
            data={
                "name": "Chris",
                "country": "No Such Zealand",
                "fantasy_country": "Neverland",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["country"], ['"No Such Zealand" is not a valid choice.']
        )

    def test_multi_serialize(self):
        mc = MultiCountry(countries="NZ,AU")
        serializer = MultiCountrySerializer(mc)
        self.assertEqual(serializer.data, {"countries": ["AU", "NZ"]})

    def test_multi_serialize_empty(self):
        mc = MultiCountry(countries="")
        serializer = MultiCountrySerializer(mc)
        self.assertEqual(serializer.data, {"countries": []})

    def test_multi_deserialize(self):
        serializer = MultiCountrySerializer(data={"countries": ["NZ", "AU"]})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["countries"], ["NZ", "AU"])

    def test_multi_deserialize_by_name(self):
        serializer = MultiCountrySerializer(
            data={"countries": ["New Zealand", "Australia"]}
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["countries"], ["NZ", "AU"])

    def test_multi_deserialize_invalid(self):
        serializer = MultiCountrySerializer(data={"countries": ["NZ", "BAD", "AU"]})
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors["countries"]
        if isinstance(errors, dict):
            # djangorestframework >= 3.8.0 returns errors as dict
            # with integers as keys
            errors = errors[1]
        self.assertEqual(errors, ['"BAD" is not a valid choice.'])

    def test_multi_deserialize_save(self):
        serializer = MultiCountrySerializer(data={"countries": ["NZ", "AU"]})
        self.assertTrue(serializer.is_valid())
        saved = serializer.save()
        loaded = MultiCountry.objects.get(pk=saved.pk)
        self.assertEqual(loaded.countries, [Country("AU"), Country("NZ")])

    def test_deserialize_blank_invalid(self):
        serializer = PersonSerializer(data={"name": "Chris", "country": ""})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["country"], ['"" is not a valid choice.'])


class TestDRFMetadata(TestCase):
    """
    Tests against the DRF OPTIONS API metadata endpoint.
    """

    @pytest.mark.skipif(not settings.USE_I18N, reason="No i18n")
    def test_actions(self):
        class ExampleView(views.APIView):
            """Example view."""

            def post(self, request):
                pass  # pragma: no cover

            def get_serializer(self):
                return PersonSerializer()

        def _choices(response, key):
            """Helper method for unpacking response JSON."""
            return response.data["actions"]["POST"][key]["choices"]

        view = ExampleView.as_view()

        factory = APIRequestFactory()
        request = factory.options("/")
        response = view(request=request)
        country_choices = _choices(response, "country")
        fantasy_choices_en = _choices(response, "fantasy_country")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(country_choices, countries_display(countries))
        self.assertEqual(fantasy_choices_en, countries_display(FantasyCountries()))

        with override_settings(LANGUAGE_CODE="fr"):
            response = view(request=request)
            fantasy_choices_fr = _choices(response, "fantasy_country")
            self.assertNotEqual(fantasy_choices_en, fantasy_choices_fr)
