#!/usr/bin/env python3

# standard
from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser
import logging
from logging.handlers import SysLogHandler
import os
import os.path
import sys
from urllib.parse import parse_qs, urlparse
import webbrowser

# external
import appdirs
import onedrivesdk
import onedrivesdk.session
from overrides import overrides

app_name = 'lsync'

syslog_handler = SysLogHandler(address = '/dev/log')
syslog_handler.ident = app_name + ': '

logger = logging.getLogger('MyLogger')
logger.setLevel(logging.DEBUG)
logger.addHandler(syslog_handler)

class Error (Exception):
    def __str__(self):
        return ' '.join(self.args)

class NoFileConfigFound (Error):
    pass

# FIXME: proper permissions for sensitive data such as session
class FileConfig:

    def __init__(self, folder):
        self.path = os.path.join(
            appdirs.user_config_dir(appname = app_name),
            folder)

    def set(self, filename, value):
        os.makedirs(self.path, exist_ok = True)

        with open(os.path.join(self.path, filename), 'w') as config:
            print(value, file = config, end = '')

    def get(self, filename):
        try:
            with open(os.path.join(self.path, filename), 'r') as config:
                return config.read()
        except FileNotFoundError:
            return None

class Client (metaclass = ABCMeta):
    @abstractmethod
    def authenticate_session(self):
        pass

    @abstractmethod
    def authenticate_url(self, url):
        pass

    @abstractmethod
    def login(self):
        pass

class OneDriveFileConfigSession (onedrivesdk.session.Session):

    # FIXME: reuse name from services command line?
    config = FileConfig('onedrive')

    @overrides
    def save_session(self, **save_session_kwargs):
        logger.debug('Saving session')

        # FIXME: refactor config key names as @property?
        self.config.set('token-type', self.token_type)
        self.config.set('expires-at', str(int(self._expires_at)))
        self.config.set('scopes', '\n'.join(self.scope))
        self.config.set('access-token', self.access_token)
        self.config.set('client-id', self.client_id)
        self.config.set('auth-server-url', self.auth_server_url)
        self.config.set('redirect-uri', self.redirect_uri)

        if self.refresh_token is not None:
            self.config.set('refresh-token', self.refresh_token)

        if self.client_secret is not None:
            self.config.set('client-secret', self.client_secret)

    @staticmethod
    @overrides
    def load_session(**load_session_kwargs):
        logger.debug('Loading session')

        config = OneDriveFileConfigSession.config
        expires_at = config.get('expires-at')

        if expires_at is None:
            logger.warning('Assuming no session, no expires-at config found')
            raise NoFileConfigFound()

        session = OneDriveFileConfigSession(
            token_type = config.get('token-type'),
            expires_in = '0',
            scope_string = ' '.join(config.get('scopes').splitlines()),
            access_token = config.get('access-token'),
            client_id = config.get('client-id'),
            auth_server_url = config.get('auth-server-url'),
            redirect_uri = config.get('redirect-uri'),
            refresh_token = config.get('refresh-token'),
            client_secret = config.get('client-secret'))

        session._expires_at = int(expires_at)
        return session

# FIXME: refresh token based on expires-at
class OneDriveClient (Client):

    def __init__(self,
            client_id = '8eaa14b1-642c-4085-a308-82cdc21e32eb',
            client_secret = None,
            api_base_url = 'https://api.onedrive.com/v1.0/',
            redirect_url = 'https://login.microsoftonline.com/common/oauth2/nativeclient',
            scopes = ('wl.signin', 'wl.offline_access', 'onedrive.readwrite'),
            http_provider = None,
            session_type = OneDriveFileConfigSession):

        if http_provider is None:
            http_provider = onedrivesdk.HttpProvider()

        self.client_secret = client_secret
        self.redirect_url = redirect_url

        self.auth_provider = onedrivesdk.AuthProvider(
            http_provider = http_provider,
            client_id = client_id,
            scopes = scopes,
            session_type = session_type)

        self.client = onedrivesdk.OneDriveClient(
            api_base_url, self.auth_provider, http_provider)

    @overrides
    def authenticate_session(self):
        logger.debug('Authenticating from saved session')

        self.auth_provider.load_session()
        self.auth_provider.refresh_token()

    @overrides
    def authenticate_url(self, url):
        logger.debug('Authenticating from auth URL')

        try:
            parsed_url = urlparse(url)
        except ValueError:
            raise Error('Invalid authentication URL:', url)

        auth_code = parse_qs(parsed_url.query).get('code')

        if auth_code is None:
            raise Error('No authentication code found in URL:', url)

        self.auth_provider.authenticate(
            auth_code, self.redirect_url, self.client_secret)
        self.auth_provider.save_session()

    def list_changes(self):
        logger.debug('Listing changes')

        # FIXME: persist token from last check and at which file for resume
        token = None

        collection_page = self.client.item(id = 'root').delta(token).get()

        for item in collection_page:
            print('-', item.id, item.name, item.parent_reference.path)

        print('#', collection_page.token)
        print('#', collection_page.next_page_link)
        print('#', collection_page.delta_link)

    @overrides
    def login(self):
        logger.debug('Opening browser for user login')
        webbrowser.open(self.auth_provider.get_auth_url(self.redirect_url))

services = {'onedrive': OneDriveClient}

def do_login_command(args):
    client = services[args.service]()

    if args.auth_url is None:
        client.login()
    else:
        client.authenticate_url(args.auth_url)

def do_start_command(args):
    client = services[args.service]()
    client.authenticate_session()
    client.list_changes()

if __name__ == "__main__":
    logger.debug('Parsing arguments')

    parser = ArgumentParser()
    command_parser = parser.add_subparsers(dest = 'command')
    command_parser.required = True

    login_parser = command_parser.add_parser('login', help = 'login to service')
    login_parser.add_argument('service', help = 'service', choices = services)
    login_parser.add_argument('auth_url', help = 'authentication URL', nargs = '?')
    login_parser.set_defaults(func = do_login_command)

    start_parser = command_parser.add_parser('start', help = 'start sync')
    start_parser.add_argument('service', help = 'service', choices = services)
    start_parser.set_defaults(func = do_start_command)

    args = parser.parse_args()

    try:
        args.func(args)
    except Error as error:
        sys.exit(str(error))

# from boxsdk import OAuth2, Client
#
# # FIXME: handle client secret storage
# import os
#
# oauth = OAuth2(
#     client_id = os.environ['BOX_API_CLIENT_ID'],
#     client_secret = os.environ['BOX_API_CLIENT_SECRET'],
#     access_token = None,
#     refresh_token = None)
#
# auth_url, csrf_token = oauth.get_authorization_url('https://api.box.com/oauth2')
# print(auth_url)
# print(csrf_token)
#
# # FIXME: allow URL
# # FIXME: verify CSRF
# auth_code = input('Paste your code here: ')
#
# # FIXME: save session
# # FIXME: handle deny
# access_token, refresh_token = oauth.authenticate(auth_code)
#
# print('access token', access_token)
# print('refresh token', refresh_token)
#
# client = Client(oauth)
# root_folder = client.folder(folder_id='0').get()
# print('folder owner: ' + root_folder.owned_by['login'])
# print('folder name: ' + root_folder['name'])
#
# # FIXME: get changes
# print(root_folder.get_items(limit=100, offset=0))
