from __future__ import unicode_literals
import logging

from django.core.mail.message import EmailMessage

from sorl.thumbnail.conf import settings


class ThumbnailLogHandler(logging.Handler):
    """
    An exception log handler for thumbnail errors.
    """

    def emit(self, record):
        import traceback

        if not settings.ADMINS:
            return
        try:
            # Hack to try to get request from context
            request = record.exc_info[2].tb_frame.f_locals['context']['request']
            request_repr = repr(request)
            request_path = request.path
        except Exception:
            request_repr = "Request unavailable"
            request_path = 'Unknown URL'
        if record.exc_info:
            stack_trace = '\n'.join(traceback.format_exception(*record.exc_info))
        else:
            stack_trace = 'No stack trace available'
        message = "%s\n\n%s" % (stack_trace, request_repr)
        msg = EmailMessage(
            '[sorl-thumbnail] %s: %s' % (record.levelname, request_path),
            message,
            settings.SERVER_EMAIL,
            [a[1] for a in settings.ADMINS],
            connection=None
        )
        msg.send(fail_silently=True)
