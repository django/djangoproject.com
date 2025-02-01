from copy import deepcopy

from django.apps import apps
from django.db import connections, models

# There's more models with a fake composite pk, but we don't test them at the moment.
_MODELS_WITH_FAKE_COMPOSITE_PK = {"ticketcustom"}


def _get_pk_field(model):
    """
    Return the pk field for the given model.
    Raise ValueError if none or more than one is found.
    """
    pks = [field for field in model._meta.get_fields() if field.primary_key]
    if len(pks) == 0:
        raise ValueError(f"No primary key field found for model {model._meta.label}")
    elif len(pks) > 1:
        raise ValueError(
            f"Found more than one primary key field for model {model._meta.label}"
        )
    else:
        return pks[0]


def _replace_primary_key_field_with_autofield(model, schema_editor):
    """
    See section about composite pks in the docstring for models.py to get some context
    for this.

    In short, some models define a field as `primary_key=True` but that field is not
    actually a primary key. In particular that field is not supposed to be unique, which
    interferes with our tests.

    For those models, we remove the `primary_key` flag from the field, and we add a
    new `testid` autofield. This makes the models easier to manipulate in the tests.
    """
    old_pk_field = _get_pk_field(model)
    del old_pk_field.unique
    new_pk_field = deepcopy(old_pk_field)
    new_pk_field.primary_key = False
    schema_editor.alter_field(
        model=model, old_field=old_pk_field, new_field=new_pk_field
    )

    autofield = models.AutoField(primary_key=True)
    autofield.set_attributes_from_name("testid")
    schema_editor.add_field(model=model, field=autofield)


def _create_db_table_for_model(model, schema_editor):
    """
    Use the schema editor API to create the db table for the given (unmanaged) model.
    """
    schema_editor.create_model(model)
    if model._meta.model_name in _MODELS_WITH_FAKE_COMPOSITE_PK:
        _replace_primary_key_field_with_autofield(model, schema_editor)


def create_db_tables_for_unmanaged_models(schema_editor):
    """
    Create tables for all unmanaged models in the tracdb app.
    """
    appconfig = apps.get_app_config("tracdb")
    for model in appconfig.get_models():
        if model._meta.managed:
            continue
        _create_db_table_for_model(model, schema_editor)


def destroy_db_tables_for_unmanaged_models(schema_editor):
    """
    Destroy tables for all unmanaged models in the tracdb app
    """
    appconfig = apps.get_app_config("tracdb")
    for model in appconfig.get_models():
        if model._meta.managed:
            continue
        schema_editor.delete_model(model)


class TracDBCreateDatabaseMixin:
    """
    A TestCase mixin that creates test tables for all the tracdb apps.
    Make sure you have databases = {"trac"} defined on your TestCase subclass.
    """

    @classmethod
    def setUpClass(cls):
        with connections["trac"].schema_editor() as schema_editor:
            create_db_tables_for_unmanaged_models(schema_editor)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        with connections["trac"].schema_editor() as schema_editor:
            destroy_db_tables_for_unmanaged_models(schema_editor)
