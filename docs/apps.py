import certifi
from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from elasticsearch_dsl.connections import connections


class DocsConfig(AppConfig):
    name = 'docs'
    verbose_name = _('Documentation')

    def ready(self):
        super().ready()
        # Configure Elasticsearch connections for connection pooling.
        connections.configure(
            default={
                'hosts': settings.ES_HOST,
                'verify_certs': True,
                'ca_certs': certifi.where(),
                'timeout': 60.0,
            },
        )
