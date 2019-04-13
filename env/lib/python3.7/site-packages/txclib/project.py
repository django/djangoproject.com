# -*- coding: utf-8 -*-

import os
import fnmatch
import datetime
import time
import urllib3
import six

try:
    import urlparse
    from urllib import urlencode
except ImportError:  # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from requests.exceptions import HTTPError
from slugify import slugify

from txclib import web
from txclib import api
from txclib import utils
from txclib import messages
from urllib3.exceptions import SSLError
from six.moves import input
from txclib.exceptions import (
    ConfigFileError, HttpNotFound, HttpNotAuthorized, MalformedConfigFile,
    TransifexrcConfigFileError
)
from txclib.urls import API_URLS
from txclib.config import Flipdict, CERT_REQUIRED
from txclib.log import logger
from txclib.paths import native_path, posix_sep
from txclib.utils import ProjectNotInit, perform_parallel_requests


DEFAULT_PULL_URL = 'pull_file'
PULL_MODE_URL_NAME = "pull_{mode}_file"

DEFAULT_API_HOSTNAME = "https://api.transifex.com"
API_USERNAME = api.Api.USERNAME


class Project(object):
    """
    Represent an association between the local and remote project instances.
    """

    SKIP_DECODE_I18N_TYPES = ['DOCX', 'XLSX']
    FILE_FILTER = "translations<sep>%(proj)s.%(res)s<sep><lang>.%(extension)s"

    def __init__(self, path_to_tx=None, init=True):
        """Initialize the Project attributes."""
        if init:
            self._init(path_to_tx)

    def _init(self, path_to_tx=None):
        instructions = "Run 'tx init' to initialize your project first!"
        try:
            self.root = utils.get_tx_dir_path(path_to_tx)
            self.config_file = utils.get_config_file_path(self.root)
            self.config = utils.read_config_file(self.config_file)

            self.txrc_file = utils.get_transifex_file()
            self.txrc = utils.get_transifex_config(self.txrc_file)
        except ProjectNotInit:
            logger.error(instructions)
            raise
        host = self.config.get('main', 'host')
        if host.lower().startswith('https://'):
            self.conn = urllib3.connection_from_url(
                host,
                cert_reqs=CERT_REQUIRED,
                ca_certs=web.certs_file()
            )
        else:
            self.conn = urllib3.connection_from_url(host)

    def validate_config(self):
        """To ensure the json structure is correctly formed."""
        pass

    def validate_credentials(self, username, password, host=None):
        """Check if api credentials are valid."""
        try:
            api.Api(
                username=username, password=password,
                path_to_tx=self.txrc_file, host=host
            ).get('auth_check')
            return True
        except HTTPError as e:
            if e.response.status_code == 401:
                return False
            raise
        return True

    def getset_host_credentials(self, host, username=None, password=None,
                                token=None, no_interactive=False,
                                only_token=False, force=False):
        """Read .transifexrc and report user,
        pass or a token for a specific host else ask the user for input.
        If the credentials provided are different from the .transifexrc file
        ask for confirmation and update them
        """

        save = False
        config_username, config_password = None, None
        if 'TX_TOKEN' in os.environ:
            # User api info from environment variable
            password = os.environ['TX_TOKEN']
            username = API_USERNAME
            """
            We need to check if hostname info exists in the .transifexrc file
            If not, it means that this is the first time this function runs, so
            we need to create its data.
            """
            save = self._add_host_to_config_file(host)
            if save:
                logger.info("Using TX_TOKEN environment variable. Credentials "
                            "won't be saved to .transifexrc.")
                self.save()
            if token:
                # Both env and argument given, inform the user
                logger.warning(
                    "There is a token in the TX_TOKEN env variable and the "
                    "--token argument. The latter will be ignored and no "
                    "credentials will be saved to the .transifexrc file."
                )
            return username, password

        try:
            config_username = self.txrc.get(host, 'username')
            config_password = self.txrc.get(host, 'password')
        except (configparser.NoOptionError, configparser.NoSectionError):
            save = True

        if token:
            password = token
            username = API_USERNAME

        if not (username and password) and not \
               (config_username and config_password):
            username = API_USERNAME
            if not no_interactive:
                password = self._token_prompt(host)
            save = True
        elif config_username and config_password:
            if username == config_username and password == config_password:
                pass
            elif username and password:
                if force:
                    save = True
                elif not no_interactive and utils.confirm(messages.update_txrc):  # noqa
                    save = True
            else:
                username = config_username
                password = config_password

        # In the cases where we need to use the credentials with the new
        # api we can only use a token and not a password so we do an extra
        # validation and prompt the use for a token if the validation fails
        if only_token and not self.validate_credentials(username, password):
            logger.info("You need a valid API token to proceed")
            username = API_USERNAME
            password = self._token_prompt(host)
            save = True

        if save:
            self._add_host_to_config_file(host)
            self.txrc.set(host, 'username', username)
            self.txrc.set(host, 'password', password)
            self.save()
        return username, password

    def _add_host_to_config_file(self, host):
        """Check if a given host exists in .transifexrc, and if not it
        updates the file with the appropriate info.

        :param str host: The hostname to search for and add if needed.
        :return: True if adding a new host, nothing otherwise.
        :rtype: bool
        """
        if not self.txrc.has_section(host):
            logger.info("Updating %s file..." % self.txrc_file)
            self.txrc.add_section(host)
            self.txrc.set(host, 'hostname', host)
            self.txrc.set(host, 'api_hostname',
                          utils.DEFAULT_HOSTNAMES['api_hostname'])
            return True
        return False

    def _token_prompt(self, host):
        token = None
        COLOR = "CYAN"
        while not token:
            token = input(utils.color_text(messages.token_msg, COLOR))
            print(utils.color_text("Verifying token...", "YELLOW"))
            if not self.validate_credentials(API_USERNAME, token, host):
                logger.info(messages.token_validation_failed)
                token = None
        return token

    def set_remote_resource(self, resource, source_lang, i18n_type, host,
                            file_filter=None):
        """Method to handle the addition/configuration of a remote resource."""
        if file_filter is None:
            file_filter = self.FILE_FILTER

        if not self.config.has_section(resource):
            self.config.add_section(resource)

        p_slug, r_slug = resource.split('.', 1)
        file_filter = file_filter.replace("<sep>", r"%s" % posix_sep)
        self._set_url_info(host=host, project=p_slug, resource=r_slug)
        extension = self._extension_for(i18n_type)[1:]

        self.config.set(resource, 'source_lang', source_lang)
        self.config.set(
            resource, 'file_filter',
            file_filter % {'proj': p_slug,
                           'res': r_slug,
                           'extension': extension}
        )
        self.config.set(resource, 'type', i18n_type)
        if host != self.config.get('main', 'host'):
            self.config.set(resource, 'host', host)

    def get_resource_host(self, resource):
        """Return the host that the resource is configured to use.
        If there is no such option we return the default one.
        """
        return self.config.get('main', 'host')

    def get_resource_lang_mapping(self, resource):
        """Get language mappings for a specific resource."""
        lang_map = Flipdict()
        try:
            args = self.config.get("main", "lang_map")
            for arg in args.replace(' ', '').split(','):
                k, v = arg.split(":")
                lang_map.update({k: v})
        except configparser.NoOptionError:
            pass
        except ValueError:
            raise MalformedConfigFile(
                "Your lang map configuration is not correct.")

        res_lang_map = Flipdict()
        if self.config.has_section(resource):
            try:
                args = self.config.get(resource, "lang_map")
                for arg in args.replace(' ', '').split(','):
                    k, v = arg.split(":")
                    res_lang_map.update({k: v})
            except configparser.NoOptionError:
                pass
            except ValueError:
                raise MalformedConfigFile(
                    "Your lang map configuration is not correct.")

        # merge the lang maps and return result
        lang_map.update(res_lang_map)

        return lang_map

    def get_source_file(self, resource):
        """Get source file for a resource."""
        if self.config.has_section(resource):
            source_lang = self.config.get(resource, "source_lang")
            source_file = self.get_resource_option(resource, 'source_file')\
                or None

            if source_file is None:
                try:
                    file_filter = self.config.get(resource, "file_filter")
                    filename = file_filter.replace('<lang>', source_lang)
                    if os.path.exists(filename):
                        return native_path(filename)
                except configparser.NoOptionError:
                    pass
            else:
                return native_path(source_file)

    def get_resource_files(self, resource, xliff=False):
        """Get a dict for all files assigned to a resource.
        First we calculate the files matching the file expression and
        then we apply all translation exceptions.
        The resulting dict will be in this format:

        { 'en': 'path/foo/en/bar.po',
        'de': 'path/foo/de/bar.po',
        'es': 'path/exceptions/es.po'}

        NOTE: All paths are relative to the root of the project
        """
        tr_files = {}
        if self.config.has_section(resource):
            try:
                file_filter = self.config.get(resource, "file_filter")
            except configparser.NoOptionError:
                file_filter = "$^"
            if xliff:
                # update the file-path in case of xliff option
                file_filter += '.xlf'
            source_lang = self.config.get(resource, "source_lang")
            source_file = self.get_source_file(resource)
            matched_files = utils.get_project_files(self.root, file_filter)
            for f_path, lang in matched_files:
                if lang != source_lang:
                    f_path = os.path.relpath(f_path, self.root)
                    if f_path != source_file:
                        tr_files.update({lang: f_path})

            for (name, value) in self.config.items(resource):
                if name.startswith("trans."):
                    value = native_path(value)
                    lang = name.split('.')[1]
                    # delete language which has same file
                    if value in list(tr_files.values()):
                        keys = []
                        for k, v in six.iteritems(tr_files):
                            if v == value:
                                keys.append(k)
                        if len(keys) == 1:
                            del tr_files[keys[0]]
                        else:
                            raise Exception("Your configuration seems wrong. "
                                            "You have multiple languages "
                                            "pointing to the same file.")
                    # Add language with correct file
                    tr_files.update({lang: value})

            return tr_files

        return None

    def get_resource_option(self, resource, option):
        """Return the requested option for a specific resource

        If there is no such option, we return None
        """

        if self.config.has_section(resource):
            if self.config.has_option(resource, option):
                return self.config.get(resource, option)
        return None

    def get_resource_list(self, project=None):
        """Parse configuration file and return tuples with the following format

        [ (project_slug, resource_slug), (..., ...)]
        """

        resource_list = []
        for r in self.config.sections():
            if r == 'main':
                continue
            p_slug, r_slug = r.split('.', 1)
            if project and p_slug != project:
                continue
            resource_list.append(r)

        return resource_list

    def save(self):
        """
        Store the configuration dictionary in the .tx/config file of the
        project.
        """
        utils.save_tx_config(self.config_file, self.config)
        utils.save_txrc_file(self.txrc_file, self.txrc)

    def get_full_path(self, relpath):
        if relpath[0] == os.path.sep:
            return relpath
        else:
            return os.path.join(self.root, relpath)

    def _get_pseudo_file(self, slang, resource, file_filter):
        pseudo_file = file_filter.replace('<lang>', '%s_pseudo' % slang)
        return native_path(pseudo_file)

    def _slug_with_branch(self, resource_slug, branch):
        """ Return the resource slug prefixed by the branch name.
        """

        return '{branch}--{resource}'.format(branch=slugify(branch),
                                             resource=resource_slug)

    def pull(self, languages=None, resources=None, overwrite=True,
             fetchall=False, fetchsource=False, force=False, skip=False,
             minimum_perc=0, mode=None, pseudo=False, xliff=False, branch=None,
             parallel=False, no_interactive=False):
        """Pull all translations file from Transifex server."""
        languages = languages or []
        resources = resources or []

        self.minimum_perc = minimum_perc
        resource_list = self.get_chosen_resources(resources)
        skip_decode = False
        params = {}

        url = self._get_url_by_pull_mode(mode=mode)

        for resource in resource_list:
            logger.debug("Handling resource %s" % resource)
            self.resource = resource
            project_slug, resource_slug = resource.split('.', 1)
            if branch:
                resource_slug = self._slug_with_branch(resource_slug, branch)
            files = self.get_resource_files(resource)
            slang = self.get_resource_option(resource, 'source_lang')
            sfile = self.get_source_file(resource)
            lang_map = self.get_resource_lang_mapping(resource)
            host = self.get_resource_host(resource)
            logger.debug("Language mapping is: %s" % lang_map)
            if mode is None:
                mode = self._get_option(resource, 'mode')
            self._set_url_info(host=host, project=project_slug,
                               resource=resource_slug)
            logger.debug("URL data are: %s" % self.url_info)

            try:
                stats = self._get_stats_for_resource(
                    no_interactive=no_interactive
                )
                details_response, _ = self.do_url_request('resource_details')
            except Exception as e:
                if isinstance(e, HttpNotAuthorized):
                    logger.error("Request is not authorized.")
                    continue
                if isinstance(e, HttpNotFound):
                    msg = "Resource %s doesn't exist on the server."
                    logger.error(msg % resource)
                    continue
                if isinstance(e, SSLError) or not skip:
                    raise
                else:
                    msg = "Skipping resource %s"
                    logger.warn(msg % resource)
                    continue

            details = utils.parse_json(details_response)
            if details['i18n_type'] in self.SKIP_DECODE_I18N_TYPES:
                skip_decode = True
            try:
                file_filter = self.config.get(resource, 'file_filter')
            except configparser.NoOptionError:
                file_filter = None

            # Pull source file
            pull_languages = set([])
            new_translations = set([])

            if pseudo:
                pseudo_file = self._get_pseudo_file(
                    slang, resource, file_filter
                )
                if self._should_download(slang, stats, local_file=pseudo_file):
                    logger.info("Pulling pseudo file for resource %s (%s)." % (
                        resource,
                        utils.color_text(pseudo_file, "RED")
                    ))
                    self._download_pseudo(
                        project_slug, resource_slug, pseudo_file
                    )
                if not languages:
                    continue

            if fetchall:
                new_translations = self._new_translations_to_add(
                    files, slang, lang_map, stats, force
                )
                if new_translations:
                    msg = ("New translations found "
                           "for the following languages:%s")
                    logger.info(msg % ', '.join(new_translations))

            existing, new = self._languages_to_pull(
                languages, files, lang_map, stats, force
            )
            pull_languages |= existing
            new_translations |= new
            logger.debug("Adding to new translations: %s" % new)

            if fetchsource:
                if sfile and slang not in pull_languages:
                    pull_languages.add(slang)
                elif slang not in new_translations:
                    new_translations.add(slang)

            if pull_languages:
                prefix = "Queueing" if parallel else "Pulling"
                logger.debug("%s languages for: %s" % (prefix, pull_languages))
                msg = prefix + " translations for resource %s (source: %s)"
                if branch:
                    msg += " for branch {}".format(branch)
                if xliff:
                    msg += " [xliff format]"
                logger.info(msg % (resource, sfile))

            if xliff:
                params.update({'file': 'xliff'})

            for lang in pull_languages:
                local_lang = lang
                if lang in list(lang_map.values()):
                    remote_lang = lang_map.flip[lang]
                else:
                    remote_lang = lang
                if languages and lang not in pull_languages:
                    logger.debug("Skipping language %s" % lang)
                    continue
                if lang != slang:
                    local_file = files.get(lang, None) or files[lang_map[lang]]
                else:
                    local_file = sfile
                logger.debug("Using file %s" % local_file)

                kwargs = {
                    'lang': remote_lang,
                    'stats': stats,
                    'local_file': local_file,
                    'force': force,
                    'mode': mode,
                }

                # xliff files should be always pulled
                if not xliff and not self._should_update_translation(**kwargs):
                    msg = "Skipping '%s' translation (file: %s)."
                    logger.info(
                        msg % (utils.color_text(remote_lang, "RED"),
                               local_file)
                    )
                    continue

                if xliff:
                    local_file += ".xlf"

                if not overwrite:
                    local_file += ".new"

                logger.info(
                    " -> %s: %s" % (utils.color_text(remote_lang, "RED"),
                                    local_file)
                )
                self.do_url_request(
                    url, language=remote_lang, skip_decode=skip_decode,
                    params=params, parallel=parallel, callback=self._save_file,
                    callback_args={"local_file": local_file}
                )

            if new_translations:
                prefix = "Queueing" if parallel else "Pulling"
                msg = prefix + " new translations for resource %s (source: %s)"
                logger.info(msg % (resource, sfile))
                for lang in new_translations:
                    if lang in list(lang_map.keys()):
                        local_lang = lang_map[lang]
                    else:
                        local_lang = lang
                    remote_lang = lang
                    if file_filter:
                        local_file = os.path.relpath(
                            os.path.join(
                                self.root, native_path(
                                    file_filter.replace('<lang>', local_lang)
                                )
                            ), os.curdir
                        )
                    else:
                        trans_dir = os.path.join(self.root, ".tx", resource)
                        if not os.path.exists(trans_dir):
                            os.mkdir(trans_dir)
                        local_file = os.path.relpath(
                            os.path.join(trans_dir,
                                         '%s_translation' % local_lang,
                                         os.curdir))

                    if xliff:
                        local_file += ".xlf"

                    if lang != slang:
                        satisfies_min = self._satisfies_min_translated(
                            stats[remote_lang], mode
                        )
                        if not satisfies_min:
                            msg = "Skipping language %s due to used options."
                            logger.info(msg % lang)
                            continue
                    logger.warning(
                        " -> %s: %s" % (utils.color_text(remote_lang, "RED"),
                                        local_file)
                    )

                    self.do_url_request(
                        url, language=remote_lang, skip_decode=skip_decode,
                        params=params, parallel=parallel,
                        callback=self._save_file,
                        callback_args={"local_file": local_file}
                    )

        # Pull the queued resources
        if parallel:
            logger.info("Pulling resources...")
            perform_parallel_requests()

    def push(self, source=False, translations=False, force=False,
             resources=None, languages=None, skip=False, no_interactive=False,
             xliff=False, branch=None, parallel=False):
        """Push all the resources"""
        languages = languages or []
        resources = resources or []

        resource_list = self.get_chosen_resources(resources)
        self.skip = skip
        self.force = force

        params = {}
        if xliff:
            params.update({'file_type': 'xliff'})

        for resource in resource_list:
            push_languages = []
            project_slug, resource_slug = resource.split('.', 1)
            if branch:
                resource_slug = self._slug_with_branch(resource_slug, branch)
            files = self.get_resource_files(resource, xliff=xliff)
            slang = self.get_resource_option(resource, 'source_lang')
            sfile = self.get_source_file(resource)
            lang_map = self.get_resource_lang_mapping(resource)
            host = self.get_resource_host(resource)
            logger.debug("Language mapping is: %s" % lang_map)
            logger.debug("Using host %s" % host)
            self._set_url_info(host=host, project=project_slug,
                               resource=resource_slug)

            message = "Pushing resource {}".format(resource)
            if parallel:
                message = "Resource {} queued for push".format(resource)
            if branch:
                message += " for branch {}".format(branch)
            logger.info(message)

            stats = self._get_stats_for_resource()

            if force and not no_interactive:
                msg = ("Warning: By using --force, the uploaded files will "
                       "overwrite remote translations, even if they are newer "
                       "than your uploaded files.\nAre you sure you want to "
                       "continue?")

                if not utils.confirm(prompt=msg, default=False):
                    logger.info("Aborting...")
                    return

            if source:
                if sfile is None:
                    logger.error("You don't seem to have a proper source file "
                                 "mapping for resource %s. Try without the "
                                 "--source option or set a source file "
                                 "first and then try again." % resource)
                    continue
                # Push source file
                try:
                    push_msg = "Pushing source file (%s)"
                    if parallel:
                        push_msg = "Will queue source file (%s) for push"
                    logger.info(push_msg % sfile)
                    if not self._resource_exists(stats):
                        logger.info("Resource does not exist.  Creating...")
                        fileinfo = "%s;%s" % (resource_slug, slang)
                        filename = self.get_full_path(sfile)
                        self._create_resource(
                            resource, project_slug, fileinfo, filename,
                            branch=branch
                        )
                    self.do_url_request(
                        'push_source', multipart=True, method="PUT",
                        files=[("%s;%s" % (resource_slug, slang),
                                self.get_full_path(sfile)
                                )],
                        params=params,
                        parallel=parallel,
                    )
                except Exception as e:
                    if isinstance(e, SSLError):
                        raise
                    elif not skip:
                        logger.error("Could not upload source file. "
                                     "You can use --skip to ignore this "
                                     "error and continue the execution.")
                        raise
                    else:
                        logger.error(e)
            else:
                try:
                    self.do_url_request('resource_details')
                except Exception as e:
                    if isinstance(e, HttpNotAuthorized):
                        logger.error("Request is not authorized.")
                        continue
                    if isinstance(e, HttpNotFound):
                        msg = "Resource %s doesn't exist on the server."
                        logger.error(msg % resource)
                        continue
                    if isinstance(e, SSLError) or not skip:
                        raise

            if translations:
                # Check if given language codes exist
                if not languages:
                    push_languages = list(files.keys())
                else:
                    push_languages = []
                    for lang in languages:
                        push_languages.append(lang_map[lang]
                                              if lang in list(lang_map.keys())
                                              else lang)

                logger.debug("Languages to push are %s" % push_languages)

                # Push translation files one by one
                for lang in push_languages:
                    local_lang = lang
                    if lang in list(lang_map.values()):
                        remote_lang = lang_map.flip[lang]
                    else:
                        remote_lang = lang

                    local_file = files.get(local_lang)
                    if not local_file:
                        msg = ("Warning: No local translation file found for "
                               "language code '%s'.")
                        logger.error(msg % utils.color_text(lang, "RED"))
                        continue

                    kwargs = {
                        'lang': remote_lang,
                        'stats': stats,
                        'local_file': local_file,
                        'force': force,
                    }
                    if not self._should_push_translation(**kwargs):
                        msg = "Skipping '%s' translation (file: %s)."
                        logger.info(msg % (utils.color_text(lang, "RED"),
                                    local_file)
                                    )
                        continue

                    msg = "Pushing '%s' translations (file: %s)"
                    if parallel:
                        msg = "Queueing '%s' translations for push (file: %s)"
                    logger.warning(
                        msg % (utils.color_text(remote_lang, "RED"),
                               local_file)
                    )
                    try:
                        self.do_url_request(
                            'push_translation', multipart=True, method='PUT',
                            files=[("%s;%s" % (resource_slug, remote_lang),
                                    self.get_full_path(local_file)
                                    )], language=remote_lang,
                            params=params,
                            parallel=parallel,
                        )
                        logger.debug("Translation %s pushed." % remote_lang)
                    except utils.HttpNotFound:
                        # If the resource exists, we suppose the language code
                        # was invalid
                        if self._resource_exists(stats):
                            error_msg = ("Error: '%s' is not a valid"
                                         " language code. Please refer to"
                                         " https://www.transifex.com/"
                                         "languages/ for a list of supported"
                                         " languages in Transifex." % lang)
                        else:
                            error_msg = ("Resource hasn't been created. "
                                         "Try pushing source file.")
                        logger.error(error_msg)
                    except Exception as e:
                        if isinstance(e, SSLError):
                            raise
                        elif not skip:
                            logger.error("Could not push translations. "
                                         "You can use --skip to ignore this "
                                         "error and continue the execution.")
                            raise
                        else:
                            logger.error(e)

        # Push the queued resources
        if parallel:
            logger.info("Pushing resources...")
            perform_parallel_requests()

    def delete(self, resources=None, languages=None, skip=False, force=False):
        """Delete translations."""
        languages = languages or []
        resources = resources or []

        resource_list = self.get_chosen_resources(resources)
        self.skip = skip
        self.force = force

        if not languages:
            delete_func = self._delete_resource
        else:
            delete_func = self._delete_translations

        for resource in resource_list:
            project_slug, resource_slug = resource.split('.', 1)
            host = self.get_resource_host(resource)
            self._set_url_info(host=host, project=project_slug,
                               resource=resource_slug)
            logger.debug("URL data are: %s" % self.url_info)
            try:
                json, _ = self.do_url_request('project_details', project=self)
            except Exception as e:
                if isinstance(e, HttpNotAuthorized):
                    logger.error("Request is not authorized.")
                    continue
                if isinstance(e, HttpNotFound):
                    msg = "Resource %s doesn't exist on the server."
                    logger.error(msg % resource)
                    continue
                if isinstance(e, SSLError) or not skip:
                    raise

            project_details = utils.parse_json(json)
            stats = self._get_stats_for_resource()
            delete_func(project_details, resource, stats, languages)

    def _delete_resource(self, project_details, resource, stats, *args):
        """Delete a resource from Transifex."""
        project_slug, resource_slug = resource.split('.', 1)
        project_resource_slugs = [
            r['slug'] for r in project_details['resources']
        ]
        logger.info("Deleting resource %s:" % resource)
        if resource_slug not in project_resource_slugs:
            if not self.skip:
                msg = "Skipping: %s : Resource does not exist."
                logger.info(msg % resource)
            return
        if not self.force:
            slang = self.get_resource_option(resource, 'source_lang')
            for language in stats:
                if language == slang:
                    continue
                if int(stats[language]['translated_entities']) > 0:
                    msg = (
                        "Skipping: %s : Unable to delete resource because it "
                        "has a not empty %s translation.\nPlease use -f or "
                        "--force option to delete this resource."
                    )
                    logger.info(msg % (resource, language))
                    return
        try:
            self.do_url_request('delete_resource', method="DELETE")
            self.config.remove_section(resource)
            self.save()
            msg = "Deleted resource %s of project %s."
            logger.info(msg % (resource_slug, project_slug))
        except Exception as e:
            msg = "Unable to delete resource %s of project %s."
            logger.error(msg % (resource_slug, project_slug))
            if isinstance(e, SSLError) or not self.skip:
                raise

    def _delete_translations(self, project_details,
                             resource, stats, languages):
        """Delete the specified translations for the specified resource."""
        logger.info("Deleting translations from resource %s:" % resource)
        for language in languages:
            self._delete_translation(
                project_details, resource, stats, language
            )

    def _delete_translation(self, project_details, resource, stats, language):
        """Delete a specific translation from the specified resource."""
        project_slug, resource_slug = resource.split('.', 1)
        if language not in stats:
            if not self.skip:
                msg = "Skipping %s: Translation does not exist."
                logger.warning(msg % (language))
            return
        if not self.force:
            teams = project_details['teams']
            if language in teams:
                msg = (
                    "Skipping %s: Unable to delete translation because it is "
                    "associated with a team.\nPlease use -f or --force option "
                    "to delete this translation."
                )
                logger.warning(msg % language)
                return
            if int(stats[language]['translated_entities']) > 0:
                msg = (
                    "Skipping %s: Unable to delete translation because it "
                    "is not empty.\nPlease use -f or --force option to delete "
                    "this translation."
                )
                logger.warning(msg % language)
                return
        try:
            self.do_url_request(
                'delete_translation', language=language, method="DELETE"
            )
            msg = "Deleted %s translations of resource %s of project %s."
            logger.info(msg % (language, resource_slug, project_slug))
        except Exception as e:
            msg = "Unable to delete translation %s"
            logger.error(msg % language)
            if isinstance(e, SSLError) or not self.skip:
                raise

    def do_url_request(self, api_call, multipart=False, data=None,
                       files=None, method="GET", skip_decode=False,
                       params=None, parallel=False, no_interactive=False,
                       **kwargs):
        """Issues a url request."""
        files = files or []
        params = params or {}

        # Read the credentials from the config file (.transifexrc)
        host = self.url_info['host']
        username, passwd = self.getset_host_credentials(
            host, no_interactive=no_interactive
        )
        try:
            hostname = self.txrc.get(host, 'hostname')
        except configparser.NoSectionError:
            raise TransifexrcConfigFileError(
                "No entry found for host %s. Edit"
                " ~/.transifexrc and add the appropriate"
                " info in there." % host
            )

        # Create the Url
        kwargs['hostname'] = hostname
        kwargs.update(self.url_info)
        url = API_URLS[api_call] % kwargs

        # in case of GET we need to add xliff option as get parameter
        if params and method == 'GET':
            # update url params
            # in case we need to add extra params on a url, we first get the
            # already existing query, create a dict which will be merged with
            # the extra params and finally put it back in the url
            url_parts = list(urlparse.urlparse(url))
            query = dict(urlparse.parse_qsl(url_parts[4]))
            query.update(params)
            url_parts[4] = urlencode(query)
            url = urlparse.urlunparse(url_parts)

        if multipart:
            for info, filename in files:
                # FIXME: It works because we only pass to files argument
                # only one item
                name = os.path.basename(filename)
                data = {
                    "resource": info.split(';')[0],
                    "language": info.split(';')[1],
                    "uploaded_file": (name, open(filename, 'rb').read())
                }
                # in case of PUT we add xliff option as form data
                if method == 'PUT':
                    data.update(params)

        # Prepare the callback function and arguments
        cb = kwargs.get("callback", None)
        args = kwargs.get("callback_args", {})

        if parallel:
            return utils.queue_request(method, hostname, url, username, passwd,
                                       data, skip_decode=skip_decode,
                                       callback=cb, callback_args=args)

        return utils.make_request(
            method, hostname, url, username, passwd, data,
            skip_decode=skip_decode, callback=cb, callback_args=args
        )

    def _should_update_translation(self, lang, stats, local_file, force=False,
                                   mode=None):
        """Whether a translation should be udpated from Transifex.

        We use the following criteria for that:
        - If user requested to force the download.
        - If language exists in Transifex.
        - If the local file is older than the Transifex's file.
        - If the user requested a x% completion.

        Args:
            lang: The language code to check.
            stats: The (global) statistics object.
            local_file: The local translation file.
            force: A boolean flag.
            mode: The mode for the translation.
        Returns:
            True or False.
        """
        return self._should_download(lang, stats, local_file, force)

    def _should_add_translation(self, lang, stats, force=False, mode=None):
        """Whether a translation should be added from Transifex.

        We use the following criteria for that:
        - If user requested to force the download.
        - If language exists in Transifex.
        - If the user requested a x% completion.

        Args:
            lang: The language code to check.
            stats: The (global) statistics object.
            force: A boolean flag.
            mode: The mode for the translation.
        Returns:
            True or False.
        """
        return self._should_download(lang, stats, None, force)

    def _should_download(self, lang, stats, local_file=None, force=False,
                         mode=None):
        """Return whether a translation should be downloaded.

        If local_file is None, skip the timestamps check (the file does
        not exist locally).
        """
        try:
            lang_stats = stats[lang]
        except KeyError:
            logger.debug("No lang %s in statistics" % lang)
            return False

        satisfies_min = self._satisfies_min_translated(lang_stats, mode)
        if not satisfies_min:
            return False

        if force:
            logger.debug("Downloading translation due to -f")
            return True

        if local_file is not None:
            remote_update = self._extract_updated(lang_stats)
            if not self._remote_is_newer(remote_update, local_file):
                logger.debug("Local is newer than remote for lang %s" % lang)
                return False
        return True

    def _should_push_translation(self, lang, stats, local_file, force=False):
        """Return whether a local translation file should be
        pushed to Trasnifex.

        We use the following criteria for that:
        - If user requested to force the upload.
        - If language exists in Transifex.
        - If local file is younger than the remote file.

        Args:
            lang: The language code to check.
            stats: The (global) statistics object.
            local_file: The local translation file.
            force: A boolean flag.
        Returns:
            True or False.
        """
        if force:
            logger.debug("Push translation due to -f.")
            return True
        try:
            lang_stats = stats[lang]
        except KeyError:
            logger.debug("Language %s does not exist in Transifex." % lang)
            return True
        if local_file is not None:
            remote_update = self._extract_updated(lang_stats)
            if self._remote_is_newer(remote_update, local_file):
                msg = "Remote translation is newer than local file for lang %s"
                logger.debug(msg % lang)
                return False
        return True

    def _generate_timestamp(self, update_datetime):
        """Generate a UNIX timestamp from the argument.

        Args:
            update_datetime: The datetime in the format used by Transifex.
        Returns:
            A float, representing the timestamp that corresponds to the
            argument.
        """
        time_format = "%Y-%m-%d %H:%M:%S"
        return time.mktime(
            datetime.datetime(
                *time.strptime(update_datetime, time_format)[0:5]
            ).utctimetuple()
        )

    def _get_time_of_local_file(self, path):
        """Get the modified time of the path_.

        Args:
            path: The path we want the mtime for.
        Returns:
            The time as a timestamp or None, if the file does not exist
        """
        if not os.path.exists(path):
            return None
        return time.mktime(time.gmtime(os.path.getmtime(path)))

    def _satisfies_min_translated(self, stats, mode=None):
        """Check whether a translation fulfills the filter used for
        minimum translated percentage.

        Args:
            perc: The current translation percentage.
        Returns:
            True or False
        """
        cur = self._extract_completed(stats, mode)
        option_name = 'minimum_perc'
        if self.minimum_perc is not None:
            minimum_percent = self.minimum_perc
        else:
            global_minimum = int(
                self.get_resource_option('main', option_name) or 0
            )
            resource_minimum = int(
                self.get_resource_option(
                    self.resource, option_name
                ) or global_minimum
            )
            minimum_percent = resource_minimum
        return cur >= minimum_percent

    def _remote_is_newer(self, remote_updated, local_file):
        """Check whether the remote translation is newer that the local file.

        Args:
            remote_updated: The date and time the translation was last
                updated remotely.
            local_file: The local file.
        Returns:
            True or False.
        """
        if remote_updated is None:
            logger.debug("No remote time")
            return False
        remote_time = self._generate_timestamp(remote_updated)
        local_time = self._get_time_of_local_file(
            self.get_full_path(local_file)
        )
        logger.debug(
            "Remote time is %s and local %s" % (remote_time, local_time)
        )
        if local_time is not None and remote_time < local_time:
            return False
        return True

    @classmethod
    def _extract_completed(cls, stats, mode=None):
        """Extract the information for the translated percentage from the stats.

        Args:
            stats: The stats object for a language as returned by Transifex.
            mode: The mode of translations requested.
        Returns:
            The percentage of translation as integer.
        """
        if mode == 'reviewed':
            key = 'reviewed_percentage'
        else:
            key = 'completed'
        try:
            return int(stats[key][:-1])
        except KeyError:
            return 0

    @classmethod
    def _extract_updated(cls, stats):
        """Extract the  information for the last update of a translation.

        Args:
            stats: The stats object for a language as returned by Transifex.
        Returns:
            The last update field.
        """
        try:
            return stats['last_update']
        except KeyError:
            return None

    def _download_pseudo(self, project_slug, resource_slug, pseudo_file):
        response, charset = self.do_url_request(
            'pull_pseudo_file',
            resource_slug=resource_slug,
            project_slug=project_slug
        )
        response = utils.parse_json(response)

        base_dir = os.path.split(pseudo_file)[0]
        utils.mkdir_p(base_dir)

        with open(pseudo_file, "wb") as fd:
            fd.write(response['content'].encode("utf-8"))

    def _new_translations_to_add(self, files, slang, lang_map,
                                 stats, force=False):
        """Return a list of translations which are
        new to the local installation.
        """
        new_translations = []
        langs = list(stats.keys())
        logger.debug("Available languages are: %s" % langs)

        for lang in langs:
            lang_exists = lang in list(files.keys())
            lang_is_source = lang == slang
            mapped_lang_exists = (
                lang in lang_map and lang_map[lang] in list(files.keys())
            )
            if lang_exists or lang_is_source or mapped_lang_exists:
                continue
            if self._should_add_translation(lang, stats, force):
                new_translations.append(lang)
        return set(new_translations)

    def _get_stats_for_resource(self, no_interactive=False):
        """Get the statistics information for a resource."""
        try:
            r, charset = self.do_url_request(
                'resource_stats', no_interactive=no_interactive
            )
            logger.debug("Statistics response is %s" % r)
            stats = utils.parse_json(r)
        except utils.HttpNotFound:
            logger.debug("Resource not found, creating...")
            stats = {}
        except Exception as e:
            logger.debug(six.u(str(e)))
            raise
        return stats

    def get_chosen_resources(self, resources):
        """Get the resources the user selected.

        Support wildcards in the resources specified by the user.

        Args:
            resources: A list of resources as specified in command-line or
                an empty list.
        Returns:
            A list of resources.
        """
        configured_resources = self.get_resource_list()
        if not resources:
            return configured_resources

        selected_resources = []
        for resource in resources:
            found = False
            for full_name in configured_resources:
                if fnmatch.fnmatch(full_name, resource):
                    selected_resources.append(full_name)
                    found = True
            if not found:
                msg = "Specified resource '%s' does not exist."
                raise Exception(msg % resource)
        logger.debug("Operating on resources: %s" % selected_resources)
        return selected_resources

    def _languages_to_pull(self, languages, files, lang_map, stats, force):
        """Get a set of languages to pull.

        Args:
            languages: A list of languages the user selected in command.
            files: A dictionary of current local translation files.
        Returns:
            A tuple of a set of existing languages and new translations.
        """
        if not languages:
            pull_languages = set([])
            pull_languages |= set(files.keys())
            mapped_files = []
            for lang in pull_languages:
                if lang in lang_map.flip:
                    mapped_files.append(lang_map.flip[lang])
            pull_languages -= set(lang_map.flip.keys())
            pull_languages |= set(mapped_files)
            return (pull_languages, set([]))
        else:
            pull_languages = []
            new_translations = []
            f_langs = list(files.keys())
            for l in languages:
                if l not in f_langs and not (
                        l in lang_map and lang_map[l] in f_langs):
                    if self._should_add_translation(l, stats, force):
                        new_translations.append(l)
                else:
                    pull_languages.append(lang_map[l]
                                          if l in list(lang_map.keys())
                                          else l)
            return (set(pull_languages), set(new_translations))

    def _extension_for(self, i18n_type):
        """Return the extension used for the specified type."""
        try:
            json, charset = self.do_url_request('formats')
            res = utils.parse_json(json)
            return res[i18n_type]['file-extensions'].split(',')[0]
        except Exception as e:
            logger.warning(
                "The file extension for i18n_type %s is not found." % str(e)
            )
            return ''

    def _resource_exists(self, stats):
        """Check if resource exists.

        Args:
            stats: The statistics dict as returned by Tx.
        Returns:
            True, if the resource exists in the server.
        """
        return bool(stats)

    def _create_resource(self, resource, pslug, fileinfo, filename, **kwargs):
        """Create a resource.

        Args:
            resource: The full resource name.
            pslug: The slug of the project.
            fileinfo: The information of the resource.
            filename: The name of the file.
        Raises:
            URLError, in case of a problem.
        """
        method = "POST"
        api_call = 'create_resource'

        host = self.url_info['host']
        try:
            hostname = self.txrc.get(host, 'hostname')
            username, passwd = self.getset_host_credentials(host)
        except configparser.NoSectionError:
            raise TransifexrcConfigFileError(
                "No user credentials found for host %s. Edit "
                "~/.transifexrc and add the appropriate "
                "info in there." % host)

        # Create the Url
        kwargs['hostname'] = hostname
        kwargs.update(self.url_info)
        kwargs['project'] = pslug
        url = (API_URLS[api_call] % kwargs)

        i18n_type = self._get_option(resource, 'type')
        if i18n_type is None:
            raise ConfigFileError(
                "Please define the resource type in "
                ".tx/config (eg. type = PO). "
                "More info: http://bit.ly/txcconfig"
            )

        name = os.path.basename(filename)
        data = {
            "slug": fileinfo.split(';')[0],
            "name": fileinfo.split(';')[0],
            "uploaded_file": (name, open(filename, 'rb').read()),
            "i18n_type": i18n_type
        }
        if kwargs.get('branch'):
            data.update({'category': kwargs['branch']})

        r, charset = utils.make_request(
            method, hostname, url, username, passwd, data
        )
        return r

    def _get_url_by_pull_mode(self, mode):
        """Get the URL by the pull mode.

        If the pull mode is not valid, the default pull mode will be used.
        """
        if mode is not None:
            try:
                # check if specific url name exists in the url list
                API_URLS[PULL_MODE_URL_NAME.format(mode=mode)]
                return PULL_MODE_URL_NAME.format(mode=mode)
            except KeyError:
                logger.warning('Invalid mode provided. ' +
                               'Default pull mode will be used')

        return DEFAULT_PULL_URL

    def _get_option(self, resource, option):
        """Get the value for the option in the configuration file.

        If the option is not in the resource section, look for it in
        the project.

        Args:
            resource: The resource name.
            option: The option the value of which we are interested in.
        Returns:
            The option value or None, if it does not exist.
        """
        value = self.get_resource_option(resource, option)
        if value is None:
            if self.config.has_option('main', option):
                return self.config.get('main', option)
        return value

    def set_i18n_type(self, resources, i18n_type):
        """Set the type for the specified resources."""
        self._set_resource_option(resources, key='type', value=i18n_type)

    def set_min_perc(self, resources, perc):
        """Set the minimum percentage for the resources."""
        self._set_resource_option(resources, key='minimum_perc', value=perc)

    def set_default_mode(self, resources, mode):
        """Set the default mode for the specified resources."""
        self._set_resource_option(resources, key='mode', value=mode)

    def _set_resource_option(self, resources, key, value):
        """Set options in the configuration file.

        If resources is empty. set the option globally.
        """
        if not resources:
            self.config.set('main', key, value)
            return
        for r in resources:
            self.config.set(r, key, value)

    @staticmethod
    def _save_file(local_file="", charset=None, data=None):
        base_dir = os.path.split(local_file)[0]
        utils.mkdir_p(base_dir)
        fd = open(local_file, 'wb')
        if charset is not None:
            data = data.encode(charset)
        fd.write(data)
        fd.close()

    def _set_url_info(self, host, project, resource):
        self.url_info = {
            'host': host,
            'project': project,
            'resource': resource
        }
