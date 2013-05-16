from south.db import dbs
from south.v2 import SchemaMigration

#
# Create a database view for "bouncing" tickets - tickets that change their
# state from closed back to open, possibly a number of times.
#

class Migration(SchemaMigration):
    viewname = "bouncing_tickets"
    viewquery = """
        SELECT
           ticket.id,
           ticket.summary,
           COUNT(*) AS times_reopened,
           MAX(change.time) AS last_reopen_time
        FROM ticket_change AS change
        JOIN ticket ON change.ticket = ticket.id
        WHERE
           change.field = 'status'
           AND change.oldvalue = 'closed'
           AND change.newvalue != 'closed'
           AND ticket.resolution = 'wontfix'
        GROUP BY ticket.id;
    """

    def forwards(self, orm):
        db = dbs['trac']
        db.execute("CREATE VIEW %s AS %s" % (self.viewname, self.viewquery))
        db.execute('COMMIT')

    def backwards(self, orm):
        db = dbs['trac']
        db.execute("DROP VIEW %s" % self.viewname)
        db.execute('COMMIT')
