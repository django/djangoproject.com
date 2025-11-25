from django.apps import AppConfig


class MoneyConfig(AppConfig):
    name = "djmoney"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        try:
            from .contrib.django_rest_framework import register_money_field

            register_money_field()
        except ImportError:
            pass
        from djmoney.admin import setup_admin_integration

        setup_admin_integration()
