from django.dispatch import Signal

updated = Signal(providing_args=['notification', 'request', 'links'])
