#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from urllib3.exceptions import SSLError

from txclib import utils
from txclib.log import set_log_level, logger
from txclib.parsers import tx_main_parser
from txclib.exceptions import AuthenticationError


# use pyOpenSSL if available
try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass


# This block ensures that ^C interrupts are handled quietly.
try:
    import signal

    def exithandler(signum, frame):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        sys.exit(1)

    signal.signal(signal.SIGINT, exithandler)
    signal.signal(signal.SIGTERM, exithandler)
    if hasattr(signal, 'SIGPIPE'):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

except KeyboardInterrupt:
    sys.exit(1)

# In python 3 default encoding is utf-8
if sys.version_info < (3, 0):
    reload(sys)  # WTF? Otherwise setdefaultencoding doesn't work
    # When we open file with f = codecs.open we specify
    # FROM what encoding to read.
    # This sets the encoding for the strings which are created with f.read()
    sys.setdefaultencoding('utf-8')


def main(argv=None):
    """
    Here we parse the flags (short, long) and we instantiate the classes.
    """
    parser = tx_main_parser()
    options, rest = parser.parse_known_args()
    if not options.command:
        parser.print_help()
        sys.exit(1)

    utils.DISABLE_COLORS = options.color_disable

    # set log level
    if options.quiet:
        set_log_level('WARNING')
    elif options.debug:
        set_log_level('DEBUG')

    # find .tx
    path_to_tx = options.root_dir or utils.find_dot_tx()

    cmd = options.command
    try:
        utils.exec_command(cmd, rest, path_to_tx)
    except SSLError as e:
        logger.error("SSL error %s" % e)
    except utils.UnknownCommandError:
        logger.error("Command %s not found" % cmd)
    except AuthenticationError:
        authentication_failed_message = """
Error: Authentication failed. Please make sure your credentials are valid.
For more information, visit:
https://docs.transifex.com/client/client-configuration#-transifexrc.
"""
        logger.error(authentication_failed_message)
    except Exception as e:
        import traceback
        if options.trace:
            traceback.print_exc()
        else:
            msg = "Unknown error" if not str(e) else str(e)
            logger.error(msg)
    # The else statement will be executed only if the command raised no
    # exceptions. If an exception was raised, we want to return a non-zero exit
    # code
    else:
        return
    sys.exit(1)


if __name__ == "__main__":
    # sys.argv[0] is the name of the script that we’re running.
    main()
