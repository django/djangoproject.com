"""
DB router for Trac. Very simple: just makes sure that all Trac tables are
queries against the "trac" DB alias.

It's very simplistic, leaving off allow_relation and allow_syncdb since all
the Trac apps are unmanaged.
"""
from unipath import FSPath as Path

THIS_APP = Path(__file__).parent.name


class TracRouter(object):
    def db_for_read(self, model, **hints):
        return 'trac' if app_label(model) == THIS_APP else None

    def db_for_write(self, model, **hints):
        return 'trac' if app_label(model) == THIS_APP else None

    def allow_syncdb(self, db, model):
        return False if db == 'trac' else None


def app_label(model):
    return model._meta.app_label
