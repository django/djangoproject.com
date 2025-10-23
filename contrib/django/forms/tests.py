from random import randint
from unittest import TestCase

from django.forms import Form, fields

from .boundfields import BoundFieldWithCharacterCounter


class BoundFieldWithCharacterCounterTests(TestCase):

    @classmethod
    def prepare_sample_form_class(cls, max_length=None):
        class SampleFormContainsBoundFieldWithCharacterCounter(Form):
            content = fields.CharField(
                max_length=max_length,
                bound_field_class=BoundFieldWithCharacterCounter,
            )

            class Meta:
                fields = ["content"]

        return SampleFormContainsBoundFieldWithCharacterCounter

    @classmethod
    def prepare_sample_bound_field(cls, max_length=None, content=None):
        form_class = cls.prepare_sample_form_class(max_length=max_length)
        form = form_class(data={"content": content})
        bound_field = form.fields["content"].get_bound_field(form, "content")
        return bound_field

    def test_get_characters_remaining_count_is_callable(self):
        bound_field = self.__class__.prepare_sample_bound_field()
        self.assertTrue(
            hasattr(bound_field, "get_characters_remaining_count"),
            "Bound field does not have `get_characters_remaining_count` method",
        )
        self.assertTrue(
            callable(bound_field.get_characters_remaining_count),
            "Expected `get_characters_remaining_count` to be callable, but it's not",
        )

    def test_characters_remaining_count_without_max_length(self):
        bound_field = self.__class__.prepare_sample_bound_field(max_length=None)
        remaining_count = bound_field.get_characters_remaining_count()
        self.assertIsNone(remaining_count)

    def test_characters_remaining_count_with_max_length(self):
        max_length = randint(0, 20)
        bound_field = self.__class__.prepare_sample_bound_field(max_length=max_length)
        remaining_count = bound_field.get_characters_remaining_count()
        self.assertGreaterEqual(remaining_count, 0)
        self.assertEqual(remaining_count, max_length)

    def test_characters_remaining_is_negative_when_content_exceeds_max_length(self):
        max_length = randint(0, 20)
        content_length = max_length + 1
        content = "*" * content_length
        bound_field = self.__class__.prepare_sample_bound_field(
            max_length=max_length,
            content=content,
        )
        remaining_count = bound_field.get_characters_remaining_count()
        self.assertLess(remaining_count, 0)
        self.assertEqual(remaining_count, max_length - content_length)

    def test_characters_remaining_matches_client_side_js_implementation(self):
        ending = "\r\n\r\r\n"
        max_length = randint(0, 20)
        visual_content_length = max_length - len(ending)
        visual_content = "*" * visual_content_length
        content = visual_content + ending
        normalized_ending = ending.replace("\r\n", "\n").replace("\r", "\n")
        normalized_content = visual_content + normalized_ending
        bound_field = self.__class__.prepare_sample_bound_field(
            max_length=max_length,
            content=content,
        )
        remaining_count = bound_field.get_characters_remaining_count()
        self.assertGreater(remaining_count, 0)
        self.assertEqual(remaining_count, max_length - len(normalized_content))
