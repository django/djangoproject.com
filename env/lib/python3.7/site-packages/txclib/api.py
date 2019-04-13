import six
import requests

from requests.auth import HTTPBasicAuth

from txclib import utils
from txclib.urls import API_URLS, HOSTNAMES
from txclib.log import logger


class Api(object):

    USERNAME = 'api'
    VALID_CALLS = ['auth_check', 'projects', 'organizations', 'formats']

    def map_paths_to_hostnames(cls, path_to_tx, host):
        domains = utils.get_api_domains(path_to_tx, host)
        return {
            path: domains[key] for key, paths in HOSTNAMES.items()
            for path in paths
        }

    def __init__(self, token=None, username=None, password=None,
                 path_to_tx=None, host=None):
        self.hostnames = self.map_paths_to_hostnames(path_to_tx, host)
        if token:
            self.token = token
            self.username = self.USERNAME
        elif username and password:
            self.token = password
            self.username = username
        else:
            logger.error("Authorization credentials are missing. Make sure "
                         "that you have run `tx init` to setup your "
                         "credentials.")

    def get(self, api_call, *args, **kwargs):
        """
        Performs the GET API call specified by api_call and
        parses the response
        """
        # mock response
        if api_call not in self.VALID_CALLS:
            raise Exception(
                "Tried to perform unsupported API call {}".format(
                    api_call
                )
            )

        hostname = self.hostnames[api_call]
        url = API_URLS[api_call] % kwargs
        url = "{}{}".format(hostname, url)

        try:
            response = requests.get(
                url, auth=HTTPBasicAuth(self.username, self.token)
            )
            response.raise_for_status()
            all_data = response.json()
        except Exception as e:
            logger.debug(six.u(str(e)))
            raise

        next_page = response.links.get('next')
        while next_page:
            try:
                response = requests.get(
                    next_page['url'],
                    auth=HTTPBasicAuth(self.USERNAME, self.token)
                )
                response.raise_for_status()
                all_data.extend(response.json())
                next_page = response.links.get('next')
            except Exception as e:
                logger.debug(six.u(str(e)))
                raise
        return all_data
