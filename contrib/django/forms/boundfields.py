from contextlib import suppress

from django.forms.boundfield import BoundField


class BoundFieldWithCharacterCounter(BoundField):

    def get_characters_remaining_count(self):
        characters_remaining_count = None
        max_length = None
        with suppress(TypeError, ValueError):
            max_length = int(self.field.max_length)
        if isinstance(max_length, int):
            value = self.value()
            if value is None:
                return max_length

            # Sometimes, when this method runs, Django may not have normalized
            # the value yet, so it causes length mismatch between the server
            # and the browser, because of the line ending characters.
            #
            # Ensure the value is normalized.
            value = value.replace("\r\n", "\n").replace("\r", "\n")

            characters_remaining_count = max_length - len(value)
        return characters_remaining_count
