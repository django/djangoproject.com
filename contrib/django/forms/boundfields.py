from contextlib import suppress
from django.forms.boundfield import BoundField


class BoundFieldWithCharacterCounter(BoundField):

    def get_characters_remaining_count(self):
        characters_remaining_count = None
        max_length = None
        with suppress(TypeError, ValueError):
            max_length = int(self.field.max_length)
        if isinstance(max_length, int):
            value = self.value().replace("\r\n", "\n").replace("\r", "\n")
            characters_remaining_count = max_length - len(value)
        return characters_remaining_count
