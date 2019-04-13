from __future__ import unicode_literals
import functools
import os
import sys
import re
import errno
import urllib3
import collections
import six
import platform
import txclib

try:
    from json import loads as parse_json
except ImportError:
    from simplejson import loads as parse_json
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

try:
    from urlparse import urljoin  # Python 2
except ImportError:
    from urllib.parse import urljoin  # Python 3

from email.parser import Parser
from urllib3.exceptions import SSLError, HTTPError
from six.moves import input
from threading import Thread, current_thread, _MainThread
from txclib.urls import API_URLS
from txclib.exceptions import (
    UnknownCommandError, HttpNotFound, HttpNotAuthorized,
    AuthenticationError, TXConnectionError, MalformedConfigFile
)
from txclib.paths import posix_path, native_path, posix_sep
from txclib.web import user_agent_identifier, certs_file
from txclib.log import logger
from txclib.config import OrderedRawConfigParser, CERT_REQUIRED
from txclib.processors import visit_hostname


class ProjectNotInit(Exception):
    pass


DEFAULT_HOSTNAMES = {
    'hostname': 'https://www.transifex.com',
    'api_hostname': 'https://api.transifex.com'
}

THREADS = []


def get_base_dir():
    """PyInstaller Run-time Operation.

    http://pythonhosted.org/PyInstaller/#run-time-operation
    """
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        basedir = os.path.join(sys._MEIPASS, 'txclib')
    else:
        # we are running in a normal Python environment
        basedir = os.path.dirname(os.path.abspath(__file__))
    return basedir


def find_dot_tx(path=os.path.curdir, previous=None):
    """Return the path where .tx folder is found.

    The 'path' should be a DIRECTORY.
    This process is functioning recursively from the current directory to each
    one of the ancestors dirs.
    """
    path = os.path.abspath(path)
    if path == previous:
        return None
    joined = os.path.join(path, ".tx")
    if os.path.isdir(joined):
        return path
    else:
        return find_dot_tx(os.path.dirname(path), path)


#################################################
# Parse file filter expressions and create regex

def regex_from_filefilter(file_filter, root_path=os.path.curdir):
    """Create proper regex from <lang> expression."""
    # Force expr to be a valid regex expr (escaped) but keep <lang> intact
    expr_re = re.escape(
        posix_path(os.path.join(root_path, native_path(file_filter)))
    )
    expr_re = expr_re.replace("\\<lang\\>", '<lang>').replace(
        '<lang>', '([^%(sep)s]+)' % {'sep': re.escape(posix_sep)})

    return "^%s$" % expr_re


TX_URLS = collections.OrderedDict([
    ('resource', '(?P<hostname>https?://(\w|\.|:|-)+)/projects/p/(?P<project>(\w|-)+)/resource/(?P<resource>(\w|-)+)/?$'),  # noqa
    ('project', '(?P<hostname>https?://(\w|\.|:|-)+)/projects/p/(?P<project>(\w|-)+)/?$'),  # noqa
    ('project2', '(?P<hostname>https?://(\w|\.|:|-)+)/(\w|-)+/(?P<project>(\w|-)+)(/(dashboard|settings))?/?'),  # noqa
    ('resource2', '(?P<hostname>https?://(\w|\.|:|-)+)/(\w|-)+/(?P<project>(\w|-)+)/(?P<resource>(\w|-)+)/?'),  # noqa
])


def parse_tx_url(url):
    """
    Try to match given url to any of the valid url patterns specified in
    TX_URLS. If not match is found, we raise exception
    """
    for type_ in list(TX_URLS.keys()):
        pattern = TX_URLS[type_]
        m = re.match(pattern, url)
        if m:
            return type_, m.groupdict()
    raise Exception(
        "tx: Malformed URL given."
        " Please refer to our docs: http://bit.ly/txcconfig"
    )


def determine_charset(response):
    content_type = response.headers.get('content-type', None)
    if content_type:
        message = Parser().parsestr("Content-type: %s" % content_type)
        for charset in message.get_charsets():
            if charset:
                return charset
    return "utf-8"


def _prepare_url_request(host, username, password):
    """
    Return a ProxyManager object (as defined in urllib3 [1]) that can be used
    to perform authorized requests to a specific host.

    Authorization header is constructed and set using "username" and "password"
    parameters. Also set the common HTTP headers that we want to be sent with
    each request.

    [1]: http://urllib3.readthedocs.io/en/latest/reference/#urllib3.poolmanager.ProxyManager  # noqa
    """
    # Initialize http and https pool managers
    num_pools = 1
    managers = {}

    if host.lower().startswith("http://"):
        scheme = "http"
        if "http_proxy" in os.environ:
            proxy_url = urllib3.util.url.parse_url(os.environ["http_proxy"])
            managers["http"] = urllib3.ProxyManager(
                proxy_url=proxy_url.url,
                proxy_headers=urllib3.util.make_headers(
                    user_agent=user_agent_identifier(),
                    proxy_basic_auth=proxy_url.auth),
                num_pools=num_pools
            )
        else:
            managers["http"] = urllib3.PoolManager(num_pools=num_pools)
    elif host.lower().startswith("https://"):
        scheme = "https"
        if "https_proxy" in os.environ:
            proxy_url = urllib3.util.url.parse_url(os.environ["https_proxy"])
            managers["https"] = urllib3.ProxyManager(
                proxy_url=proxy_url.url,
                proxy_headers=urllib3.util.make_headers(
                    user_agent=user_agent_identifier(),
                    proxy_basic_auth=proxy_url.auth),
                num_pools=num_pools,
                cert_reqs=CERT_REQUIRED,
                ca_certs=certs_file()
            )
        else:
            managers["https"] = urllib3.PoolManager(
                num_pools=num_pools,
                cert_reqs=CERT_REQUIRED,
                ca_certs=certs_file()
            )
    else:
        raise Exception("Unknown scheme")

    headers = urllib3.util.make_headers(
        basic_auth='{0}:{1}'.format(username, password),
        accept_encoding=True,
        user_agent=user_agent_identifier(),
        keep_alive=True
    )

    manager = managers[scheme]

    return headers, manager


def queue_request(method, host, url, username, password, fields=None,
                  skip_decode=False, get_params=None, callback=None,
                  callback_args=None):
    """
    Add a request to the THREADS queue. Request will not be sent until the
    'perform_parallel_requests' method is called.
    """
    get_params = get_params or {}
    callback_args = callback_args or {}

    headers, manager = _prepare_url_request(host, username, password)
    # All arguments must be bytes, not unicode
    global THREADS
    THREADS.append(Thread(target=perform_single_request,
                          args=(method,
                                urljoin(host, url),
                                dict(headers),
                                fields,
                                manager,
                                skip_decode,
                                callback,
                                callback_args)))


def make_request(method, host, url, username, password, fields=None,
                 skip_decode=False, get_params=None, *args, **kwargs):
    """
    Perform a request.

    This is the (default) blocking method of making requests.
    """
    get_params = get_params or {}

    headers, manager = _prepare_url_request(host, username, password)
    # All arguments must be bytes, not unicode
    return perform_single_request(method,
                                  urljoin(host, url),
                                  dict(headers),
                                  fields,
                                  manager,
                                  skip_decode,
                                  *args,
                                  **kwargs)


def perform_parallel_requests():
    """
    Perform a set of requests in parallel using threads. The requests are saved
    in the global THREADS variable. We send requests in batches of 20 in order
    to achieve optimal performance without hitting API limits.
    """
    global THREADS

    if not THREADS:
        return

    total = len(THREADS)
    completed = 0
    update_progress(0, total)

    while THREADS:
        next_batch = THREADS[:10]
        THREADS = THREADS[10:]

        for thread in next_batch:
            thread.start()
        for thread in next_batch:
            thread.join()

        completed += len(next_batch)
        update_progress(completed, total)


def perform_single_request(method, url, headers, fields, manager, skip_decode,
                           callback=None, callback_args=None):
    callback_args = callback_args or {}
    response = None

    try:
        encoded_request = encode_args(manager.request)
        response = encoded_request(method, url, headers=headers, fields=fields)
        r_value = parse_tx_response(response, skip_decode)
    except SSLError:
        logger.error("Invalid SSL certificate")
        raise
    except HTTPError:
        logger.error("HTTP error")
        raise
    except Exception as e:
        logger.error(str(e))
        if isinstance(current_thread(), _MainThread):
            raise
        return
    finally:
        if response is not None:
            response.close()

    if callback is not None:
        callback_args.update({"data": r_value[0],
                              "charset": r_value[1]})
        callback(**callback_args)

    return r_value


def parse_tx_response(response, skip_decode):
    """
    Handle a response from the Transifex API.
    """
    charset = None
    data = response.data
    if not skip_decode:
        charset = determine_charset(response)
        if isinstance(data, bytes):
            data = data.decode(charset)
    if response.status < 200 or response.status >= 400:
        if response.status == 401:
            raise AuthenticationError(data)
        elif response.status == 403:
            raise HttpNotAuthorized(data)
        elif response.status == 404:
            raise HttpNotFound(data)
        elif response.status >= 500:
            msg = "Failed to connect. Server responded with HTTP code {}"
            raise TXConnectionError(msg.format(response.status),
                                    code=response.status)
        else:
            raise Exception("Error received from server: {}".format(data))

    return data, charset


def get_details(api_call, username, password, *args, **kwargs):
    """
    Get the tx project info through the API.
    This function can also be used to check the existence of a project.
    """
    url = API_URLS[api_call] % kwargs
    try:
        data, charset = make_request(
            'GET', kwargs['hostname'], url, username, password
        )
        return parse_json(data)
    except Exception as e:
        logger.debug(six.u(str(e)))
        raise


def valid_resource_slug(slug):
    """
    Check if a resource slug contains only valid characters.
    Valid format is [-_\w].[-_\w] (<project>.<resource>)
    """
    try:
        a, b = slug.split('.')
    except ValueError:
        return False
    else:
        return valid_slug(a) and valid_slug(b)


def valid_slug(slug):
    """
    Check if a slug contains only valid characters.
    Valid chars include [-_\w]
    """
    return re.match("^[A-Za-z0-9_-]+$", slug)


def discover_commands():
    """
    Inspect commands.py and find all available commands
    """
    import inspect
    from txclib import commands

    command_table = {}
    fns = inspect.getmembers(commands, inspect.isfunction)

    for name, fn in fns:
        if name.startswith("cmd_"):
            command_table.update({
                name.split("cmd_")[1]: fn
            })

    return command_table


def exec_command(command, *args, **kwargs):
    """
    Execute given command
    """
    commands = discover_commands()
    try:
        cmd_fn = commands[command]
    except KeyError:
        raise UnknownCommandError
    cmd_fn(*args, **kwargs)


def mkdir_p(path):
    try:
        if path:
            os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def confirm(prompt='Continue?', default=True):
    """
    Prompt the user for a Yes/No answer.
    Args:
        prompt: The text displayed to the user ([Y/n] will be appended)
        default: If the default value will be yes or no
    """
    valid_yes = ['Y', 'y', 'Yes', 'yes', ]
    valid_no = ['N', 'n', 'No', 'no', ]
    if default:
        prompt = prompt + ' [Y/n]: '
        valid_yes.append('')
    else:
        prompt = prompt + ' [y/N]: '
        valid_no.append('')

    ans = input(prompt)
    while (ans not in valid_yes and ans not in valid_no):
        ans = input(prompt)

    return ans in valid_yes


# Stuff for command line colored output

COLORS = [
    'BLACK', 'RED', 'GREEN', 'YELLOW',
    'BLUE', 'MAGENTA', 'CYAN', 'WHITE'
]

DISABLE_COLORS = False


def color_text(text, color_name, bold=False):
    """
    This command can be used to colorize command line output. If the shell
    doesn't support this or the --disable-colors options has been set, it just
    returns the plain text.
    Usage:
        print "%s" % color_text("This text is red", "RED")
    """
    if color_name in COLORS and not DISABLE_COLORS:
        return '\033[%s;%sm%s\033[0m' % (
            int(bold), COLORS.index(color_name) + 30, text)
    else:
        return text


def _can_walk(base, subdirectories):
    """
    Determine if the first element of the 'subdirectories' list can be appended
    to the 'base' path and still specify a directory.
    """
    # Always consider the last part of the subdirectories the filename
    if len(subdirectories) < 2:
        return False
    # Allow any directory name that doesn't contain the <lang> placeholder
    return "<lang>" not in subdirectories[0]


def get_project_files(curpath, expression):
    """
    Iterate over the files in the project that match the given expression.
    Return a tuple with the absolute file path and the language code of the
    language that is associated with it.
    """
    # Strip the reference to the current directory, if it exists
    if expression.startswith(".{}".format(os.sep)):
        expression = expression[2:]
    # Split the expression into parts
    expression_parts = expression.split(os.sep)
    # Merge the expression's path into 'curpath' until the <lang> placeholder
    # is specified in order to reduce the search tree
    while _can_walk(curpath, expression_parts):
        curpath = os.path.realpath(os.path.join(curpath, expression_parts[0]))
        expression_parts = expression_parts[1:]
    expr_re = regex_from_filefilter(os.path.join(*expression_parts), curpath)
    expression_regex = re.compile(expr_re)

    visited = set()
    for root, dirs, files in os.walk(curpath, followlinks=True):
        root_realpath = os.path.realpath(root)

        # Don't visit any subdirectory
        if root_realpath in visited:
            del dirs[:]
            continue

        for file_path in files:
            full_path = os.path.realpath(os.path.join(root, file_path))
            match = expression_regex.match(posix_path(full_path))
            if match:
                try:
                    lang = match.group(1)
                except IndexError:
                    msg = ("File filter '{}' does not contain the '<lang>' "
                           "placeholder".format(expression))
                    raise MalformedConfigFile(msg)
                yield full_path, lang

        visited.add(root_realpath)

        # Find which directories are already visited and remove them from
        # further processing
        removals = list(
            d for d in dirs
            if os.path.realpath(os.path.join(root, d)) in visited
        )
        for removal in removals:
            dirs.remove(removal)


def encode_args(func):
    # we have to patch func in order to make tests work.
    # sadly mock does not have the attributes needed for functools
    # so we need to set the manually
    if not hasattr(func, '__name__'):
        functools.update_wrapper(func, str.split, ('__name__', ))

    @functools.wraps(func)
    def decorated(*args, **kwargs):
        new_args = _encode_anything(args)
        new_kwargs = _encode_anything(kwargs, keys_as_unicode=True)
        return func(*new_args, **new_kwargs)
    return decorated


def _encode_anything(thing, encoding='utf-8', keys_as_unicode=False):
    # Handle python versions
    if sys.version_info.major == 3:
        return thing

    if isinstance(thing, str):
        return thing
    elif isinstance(thing, unicode):
        return thing.encode(encoding)
    elif isinstance(thing, list):
        return [_encode_anything(item) for item in thing]
    elif isinstance(thing, tuple):
        return tuple(_encode_anything(list(thing)))
    elif isinstance(thing, dict):
        # I know this is weird, but when using kwargs in python-3, the keys
        # should be str, not bytes
        if keys_as_unicode:
            return {key: _encode_anything(value)
                    for key, value in thing.items()}
        else:
            return {_encode_anything(key): _encode_anything(value)
                    for key, value in thing.items()}
    elif thing is None:
        return thing
    else:
        raise TypeError("Could not encode, unknown type: {}".
                        format(type(thing)))


def get_config_file_path(root_path):
    """Check the .tx/config file exists."""
    config_file = os.path.join(root_path, ".tx", "config")
    logger.debug("Config file is %s" % config_file)
    if not os.path.exists(config_file):
        msg = "Cannot find the config file (.tx/config)!"
        raise ProjectNotInit(msg)
    return config_file


def get_tx_dir_path(path_to_tx):
    """Check the .tx directory exists."""
    root_path = path_to_tx or find_dot_tx()
    logger.debug("Path to tx is %s." % root_path)
    if not root_path:
        msg = "Cannot find any .tx directory!"
        raise ProjectNotInit(msg)
    return root_path


def read_config_file(config_file):
    """Parse the configuration file and return its contents."""
    config = OrderedRawConfigParser()
    try:
        config.read(config_file)
    except Exception as err:
        msg = "Cannot open/parse .tx/config file: %s" % err
        raise ProjectNotInit(msg)
    return config


def get_transifex_config(txrc_file):
    """Read the configuration from the .transifexrc files."""
    txrc = OrderedRawConfigParser()
    try:
        txrc.read((txrc_file,))
    except Exception as e:
        msg = "Cannot read configuration file: %s" % e
        raise ProjectNotInit(msg)
    migrate_txrc_file(txrc_file, txrc)
    return txrc


def migrate_txrc_file(txrc_file, txrc):
    """Migrate the txrc file, if needed."""
    if not os.path.exists(txrc_file):
        return txrc
    for section in txrc.sections():
        try:
            txrc.get(section, 'api_hostname')
        except configparser.NoOptionError:
            txrc.set(section, 'api_hostname',
                     DEFAULT_HOSTNAMES['api_hostname'])

        orig_hostname = txrc.get(section, 'hostname')
        hostname = visit_hostname(orig_hostname)
        if hostname != orig_hostname:
            msg = "Hostname %s should be changed to %s."
            logger.info(msg % (orig_hostname, hostname))
            if (sys.stdin.isatty() and sys.stdout.isatty() and
                    confirm('Change it now? ', default=True)):
                txrc.set(section, 'hostname', hostname)
                msg = 'Hostname changed'
                logger.info(msg)
            else:
                hostname = orig_hostname
        save_txrc_file(txrc_file, txrc)
    return txrc


def get_transifex_file(directory=None):
    """Fetch the path of the .transifexrc file.
    It is in the home directory of the user by default.
    """
    directory = find_dot_tx()
    if directory:
        local_txrc_file = os.path.join(directory, ".transifexrc")
        if os.path.exists(local_txrc_file):
            logger.debug(".transifexrc file is at %s" % directory)
            return local_txrc_file

    directory = os.path.expanduser('~')
    txrc_file = os.path.join(directory, ".transifexrc")
    logger.debug(".transifexrc file is at %s" % directory)
    if not os.path.exists(txrc_file):
        msg = "No credentials file was found at %s." % (txrc_file)
        logger.info(msg)
        mask = os.umask(0o077)
        open(txrc_file, 'w').close()
        os.umask(mask)
        if os.path.exists(txrc_file):
            logger.info('Created %s ' % txrc_file)
        else:
            logger.info('Could not create %s ' % txrc_file)
    return txrc_file


def save_tx_config(config_file, config):
    """Save the local configuration file."""
    fh = open(config_file, "w")
    config.write(fh)
    fh.close()


def save_txrc_file(txrc_file, txrc):
    """Save the .transifexrc file."""
    mask = os.umask(0o077)
    fh = open(txrc_file, 'w')
    txrc.write(fh)
    fh.close()
    os.umask(mask)


def get_api_domains(path_to_tx, host):
    try:
        txrc = get_transifex_config(get_transifex_file(path_to_tx))
        return {
            'hostname': txrc.get(host, 'hostname'),
            'api_hostname': txrc.get(host, 'api_hostname')
        }
    except (ProjectNotInit, configparser.NoOptionError,
            configparser.NoSectionError):
        return DEFAULT_HOSTNAMES


def get_current_branch(root_dir):
    """Searches for a .git directory starting from the
    current working directory and up until the project
    root.
    Return current branch if .git exists else None
    """
    found, git_dir = None, None
    cwd = os.getcwd()
    while root_dir in cwd:
        git_dir = os.path.join(cwd, '.git')
        if os.path.isdir(git_dir):
            found = True
            break
        cwd = os.path.dirname(cwd)

    if found:
        with open(os.path.join(git_dir, 'HEAD')) as f:
            ref = f.read()
            m = re.match('ref: refs/heads/(.+?)\s+$', ref)
            if m:
                return m.group(1)


def get_version():
    return '%s, py %s.%s, %s' % (
        txclib.__version__,
        sys.version_info.major,
        sys.version_info.minor,
        platform.machine()
    )


def update_progress(done, total):
    """
    Print a graphical progress bar to indicate a progress status.
    """
    percentage = 100.0 * done / float(total)
    template = '\r[{:25}] {:>3.0f}% ({}/{})'
    sys.stdout.write(template.format("#" * int(percentage/4),
                                     percentage, done, total))
    sys.stdout.flush()

    # Print a new line when done
    if done == total:
        sys.stdout.write('\n')
