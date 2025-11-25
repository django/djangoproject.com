import json
import sys

import django
from django.core.serializers.base import DeserializationError
from django.core.serializers.json import Serializer as JSONSerializer

from djmoney.money import Money

from .models.fields import MoneyField
from .utils import get_currency_field_name


Serializer = JSONSerializer


def Deserializer(stream_or_string, **options):  # noqa
    """
    Deserialize a stream or string of JSON data.
    """
    # Local imports to allow using modified versions of `_get_model` / `_get_model_from_node`
    # It could be patched in runtime via `unittest.mock.patch` for example
    from django.core.serializers.python import Deserializer as PythonDeserializer

    if django.VERSION < (5, 2):
        from django.core.serializers.python import _get_model
    else:
        _get_model = PythonDeserializer._get_model_from_node

    ignore = options.pop("ignorenonexistent", False)

    if not isinstance(stream_or_string, (bytes, str)):
        stream_or_string = stream_or_string.read()
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode("utf-8")
    try:
        for obj in json.loads(stream_or_string):
            try:
                Model = _get_model(obj["model"])
            except DeserializationError:
                if ignore:
                    continue
                else:
                    raise
            money_fields = {}
            fields = {}
            field_names = {field.name for field in Model._meta.get_fields()}
            for field_name, field_value in obj["fields"].items():
                if ignore and field_name not in field_names:
                    # skip fields no longer on model
                    continue
                field = Model._meta.get_field(field_name)
                if isinstance(field, MoneyField) and field_value is not None:
                    money_fields[field_name] = Money(
                        field_value, obj["fields"][get_currency_field_name(field_name, field)]
                    )
                else:
                    fields[field_name] = field_value
            obj["fields"] = fields

            for inner_obj in PythonDeserializer([obj], **options):
                for field, value in money_fields.items():
                    setattr(inner_obj.object, field, value)
                yield inner_obj
    except (GeneratorExit, DeserializationError):
        raise
    except Exception as exc:
        raise DeserializationError.with_traceback(DeserializationError(exc), sys.exc_info()[2])
