from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import certifi
from elasticsearch_dsl.connections import connections


class DocsConfig(AppConfig):
    name = 'docs'
    verbose_name = _('Documentation')

    def ready(self):
        super(DocsConfig, self).ready()
        # Configure Elasticsearch connections for connection pooling.
        connections.configure(
            default={
                'hosts': settings.ES_HOST,
                'verify_certs': True,
                'ca_certs': certifi.where(),
            },
        )
