from django.apps import apps
from django.db import connections


def create_db_tables_for_unmanaged_models(schema_editor):
    """
    Create tables for all unmanaged models in the tracdb app.
    """
    appconfig = apps.get_app_config("tracdb")
    for model in appconfig.get_models():
        if model._meta.managed:
            continue
        schema_editor.create_model(model)


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
