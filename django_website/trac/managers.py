from django.db import models

# Trac's custom ticket fields. Maps field names to coercion functions.
TICKET_CUSTOM = {
 'stage': unicode,
 'needs_tests': bool,
 'easy': bool,
 'ui_ux': bool,
 'needs_docs': bool,
 'has_patch': bool,
 'needs_better_patch': bool,
}

class TicketManager(models.Manager):
