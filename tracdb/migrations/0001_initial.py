# encoding: utf-8
from south.db import dbs
from south.v2 import SchemaMigration

#
# Trac uses composite primary keys, which Django doesn't understand.
# These views fix that, for certain values of "fix."
#

class Migration(SchemaMigration):
    def forwards(self, orm):
        db = dbs['trac']
        db.execute('''CREATE VIEW "attachment_django_view" AS
            SELECT "type" || '.' || "id" || '.' || "filename" AS "django_id", *
            FROM attachment;''')
        db.execute('''CREATE VIEW "wiki_django_view" AS
            SELECT "name" || '.' || "version" AS "django_id", *
            FROM wiki;''')

        # Work around a limitation of South's support for multiple databases.
        # See http://south.aeracode.org/ticket/924.
        db.execute('COMMIT')

    def backwards(self, orm):
        db = dbs['trac']
        db.execute('DROP VIEW "attachment_django_view";')
        db.execute('DROP VIEW "wiki_django_view";')
        db.execute('COMMMIT')
