"""
DB router for Trac. Very simple: just makes sure that all Trac tables are
queries against the "trac" DB alias.

It's very simplistic, leaving off allow_relation and allow_migrate since all
the Trac apps are unmanaged.
"""
THIS_APP = 'tracdb'


class TracRouter:
    def db_for_read(self, model, **hints):
        return 'trac' if app_label(model) == THIS_APP else None

    def db_for_write(self, model, **hints):
        return 'trac' if app_label(model) == THIS_APP else None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return False if db == 'trac' else None


def app_label(model):
    return model._meta.app_label
