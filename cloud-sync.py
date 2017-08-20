#!/usr/bin/env python3

# standard
from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser
import logging
from logging import StreamHandler
from logging.handlers import SysLogHandler
import os
import os.path
import pathlib
import re
import stat
import sys
from urllib.parse import parse_qs, urlparse
import webbrowser

# external
import appdirs
import boxsdk
import boxsdk.exception
import dateutil.parser
import onedrivesdk
import onedrivesdk.session
from overrides import overrides

app_name = 'cloud-sync'

syslog_handler = SysLogHandler(address = '/dev/log')
syslog_handler.ident = app_name + ': '

logger = logging.getLogger('MyLogger')
logger.setLevel(logging.DEBUG)
logger.addHandler(syslog_handler)

class Error (Exception):
    def __str__(self):
        return ' '.join(map(str, self.args))

class FileConfig:

    def __init__(self, app_name, folder):
        self.path_template = pathlib.Path(
            appdirs.user_config_dir(appname = app_name),
            folder,
            'NAME_PLACEHOLDER')

    def set(self, filename, value, is_private = False):
        os.makedirs(str(self.path_template.parent), exist_ok = True)
        config = self.path_template.with_name(filename)
        logger.debug('Set config at %s', str(config))

        if is_private:
            config.touch(mode = stat.S_IRWXU ^ stat.S_IXUSR, exist_ok = True)

        config.write_text(value)

    def get(self, filename):
        config = self.path_template.with_name(filename)
        logger.debug('Get config at %s', str(config))

        try:
            return config.read_text()
        except FileNotFoundError:
            return None

    def unset(self, filename):
        config = str(self.path_template.with_name(filename))
        logger.debug('Unset config at %s', config)
        os.remove(config)

    def __str__(self):
        return str(self.path_template.parent)

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

    def parse_auth_url(self, url, code_param_name, csrf_param_name = None):
        logger.debug('Parse authentication URL %s', url)

        try:
            parsed_url = urlparse(url)
        except ValueError as e:
            raise Error('Invalid authentication URL:', url) from e

        query_string = parse_qs(parsed_url.query)
        auth_code = query_string.get(code_param_name)

        if auth_code is None:
            raise Error('No authentication code found in URL:', url)
        elif len(auth_code) > 1:
            raise Error('Multiple authentication codes found in URL:', url)
        else:
            [auth_code] = auth_code

        if csrf_param_name is None:
            return auth_code

        csrf_token = query_string.get(csrf_param_name)

        if csrf_token is None:
            raise Error('No CSRF token found in URL:', url)
        elif len(csrf_token) > 1:
            raise Error('Multiple CSRF tokens found in URL:', url)
        else:
            [csrf_token] = csrf_token

        return auth_code, csrf_token

class OneDriveFileConfigSession (onedrivesdk.session.Session):

    @overrides
    def save_session(self, **kwargs):
        config = kwargs['config']
        logger.debug('Save session at %s', config)

        config.set('token-type', self.token_type)
        config.set('expires-at', str(int(self._expires_at)))
        config.set('scopes', '\n'.join(self.scope))
        config.set('access-token', self.access_token, is_private = True)
        config.set('client-id', self.client_id)
        config.set('auth-server-url', self.auth_server_url)
        config.set('redirect-uri', self.redirect_uri)

        if self.refresh_token is not None:
            config.set('refresh-token', self.refresh_token,
                is_private = True)

        if self.client_secret is not None:
            config.set('client-secret', self.client_secret)

    @staticmethod
    @overrides
    def load_session(**kwargs):
        config = kwargs['config']
        logger.debug('Load session at %s', config)
        expires_at = config.get('expires-at')

        if expires_at is None:
            logger.warning('Assuming no session, no expires-at config found')
            raise Error('No authenticated session (did you login?)')

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

class OneDriveClient (Client):

    def __init__(self,
            client_id = '8eaa14b1-642c-4085-a308-82cdc21e32eb',
            client_secret = None,
            api_base_url = 'https://api.onedrive.com/v1.0/',
            redirect_url = 'https://login.microsoftonline.com/common/oauth2/nativeclient',
            scopes = ('wl.signin', 'wl.offline_access', 'onedrive.readwrite'),
            http_provider = None,
            session_type = OneDriveFileConfigSession,
            config = None):

        if http_provider is None:
            http_provider = onedrivesdk.HttpProvider()

        # FIXME: make app name and folder configurable
        if config is None:
            config = FileConfig(app_name, 'onedrive')

        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.config = config

        self.auth_provider = onedrivesdk.AuthProvider(
            http_provider = http_provider,
            client_id = client_id,
            scopes = scopes,
            session_type = session_type)

        self.client = onedrivesdk.OneDriveClient(
            api_base_url, self.auth_provider, http_provider)

    @overrides
    def authenticate_session(self):
        logger.debug('Authenticate from saved session')

        self.auth_provider.load_session(config = self.config)

        try:
            self.auth_provider.refresh_token()
        except Exception as e:
            raise Error('Authentication failed') from e

    @overrides
    def authenticate_url(self, url):
        logger.debug('Authenticate from auth URL %s', url)
        auth_code = self.parse_auth_url(url, code_param_name = 'code')

        try:
            self.auth_provider.authenticate(
                auth_code, self.redirect_url, self.client_secret)
        except Exception as e:
            raise Error('Invalid authentication code in URL:', url) from e

        self.auth_provider.save_session(config = self.config)

    @overrides
    def login(self):
        logger.debug('Open browser for user login')
        webbrowser.open(self.auth_provider.get_auth_url(self.redirect_url))

    # FIXME: persist token from last check and at which file for resuming
    # FIXME: retry/backoff mechanisms, https://paperairoplane.net/?p=640
    # FIXME: download progress for bigger files?
    # FIXME: handle network disconnects and timeouts
    # FIXME: handle Ctrl-C
    # FIXME: too big, refactor
    def download(self, folder):
        logger.debug('Download to %s', folder)
        delta_token = None

        logger.debug('List changes with delta token %s', delta_token)
        items = self.client.item(id = 'root').delta(delta_token).get()

        for item in items:
            cloud_path = os.path.join(
                re.sub('^[^:]+:', os.path.curdir, item.parent_reference.path),
                item.name)

            if self.is_root_item(item):
                logger.debug('Skip root item with ID %s at %s',
                    item.id, cloud_path)
                continue

            local_path = os.path.join(folder, cloud_path)
            logger.debug('Cloud item with ID %s', item.id)
            is_folder = item.folder

            if self.is_package_item(item):
                is_folder = True
                logger.debug('Handle package of type %s as folder %s',
                    self.get_package_item_type(item), cloud_path)

            if is_folder:
                if item.deleted:
                    logger.debug('Delete folder %s', cloud_path)
                    os.rmdir(local_path)
                else:
                    logger.debug('Create folder %s', cloud_path)
                    os.makedirs(local_path, exist_ok = True)
            else:
                if item.deleted:
                    logger.debug('Delete file %s', cloud_path)
                    os.remove(local_path)
                else:
                    logger.debug('Create file %s', cloud_path)
                    self.client.item(id = item.id).download(local_path)

            mtime = self.localize_item_last_modified_datetime(item)
            logger.debug('Set modified time to %s', mtime)
            os.utime(local_path, (mtime.timestamp(),) * 2)

    def get_package_item_type(self, item):
        return item._prop_dict['package']['type']

    def is_package_item(self, item):
        return 'package' in item._prop_dict

    def is_root_item(self, item):
        return 'root' in item._prop_dict

    def localize_item_last_modified_datetime(self, item):
        return dateutil.parser \
            .parse(item._prop_dict['lastModifiedDateTime']) \
            .astimezone()

# FIXME: download
class BoxClient (Client):

    # FIXME: handle client secret storage
    def __init__(self,
            client_id = None,
            client_secret = None,
            redirect_url = 'https://api.box.com/oauth2',
            config = None):

        if client_id is None:
            client_id = os.environ['BOX_API_CLIENT_ID']

        if client_secret is None:
            client_secret = os.environ['BOX_API_CLIENT_SECRET']

        # FIXME: make app name and folder configurable
        if config is None:
            config = FileConfig(app_name, 'box')

        self.client = None
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.config = config
        self.cached_oauth = None

    @property
    def oauth(self):
        if self.cached_oauth is None:
            self.cached_oauth = boxsdk.OAuth2(
                client_id = self.client_id,
                client_secret = self.client_secret,
                access_token = self.config.get('access-token'),
                refresh_token = self.config.get('refresh-token'),
                store_tokens = self.store_tokens)

        return self.cached_oauth

    @overrides
    def authenticate_session(self):
        logger.debug('Authenticate from saved session')
        self.client = boxsdk.Client(self.oauth)

        try:
            user = self.client.user(user_id = 'me').get()
        except boxsdk.exception.BoxException as e:
            raise Error('Authentication failed') from e

        logger.debug('Logged in as %s with ID %s', user['name'], user['id'])

    @overrides
    def authenticate_url(self, url):
        logger.debug('Authenticate from auth URL %s', url)

        auth_code, csrf_token = self.parse_auth_url(url,
            code_param_name = 'code',
            csrf_param_name = 'state')

        stored_csrf_token = self.config.get('csrf-token')

        if csrf_token != stored_csrf_token:
            raise Error('CSRF token mismatch (did you login recently?):',
                csrf_token, 'vs', stored_csrf_token)

        self.oauth.authenticate(auth_code)
        self.config.unset('csrf-token')
        self.cached_oauth = None

    @overrides
    def login(self):
        logger.debug('Open browser for user login')

        auth_url, csrf_token = self.oauth.get_authorization_url(
            self.redirect_url)

        self.config.set('csrf-token', csrf_token, is_private = True)
        webbrowser.open(auth_url)

    def store_tokens(self, access_token, refresh_token):
        self.config.set('access-token', access_token, is_private = True)
        self.config.set('refresh-token', refresh_token, is_private = True)

clients = {
    'box': BoxClient,
    'onedrive': OneDriveClient,
}

def do_login_command(args):
    client = clients[args.service]()

    if args.auth_url is None:
        client.login()
    else:
        client.authenticate_url(args.auth_url)

# FIXME: receive where to download to via command line
# FIXME: prevent overwriting existing files?
# FIXME: sandbox download folder (never modify anything outside of it)
def do_start_command(args):
    client = clients[args.service]()
    client.authenticate_session()
    client.download('foobar')

# FIXME: make logger configurable for each client
# FIXME: unit test
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-v', help = 'verbose output', action = 'store_true',
        dest = 'is_verbose')

    command_parser = parser.add_subparsers(dest = 'command')
    command_parser.required = True

    login_parser = command_parser.add_parser('login', help = 'login to service')
    login_parser.add_argument('service', help = 'service', choices = clients)
    login_parser.add_argument('auth_url',
        help = 'authentication URL', nargs = '?')
    login_parser.set_defaults(func = do_login_command)

    start_parser = command_parser.add_parser('start', help = 'start sync')
    start_parser.add_argument('service', help = 'service', choices = clients)
    start_parser.set_defaults(func = do_start_command)

    args = parser.parse_args()

    if args.is_verbose:
        logger.addHandler(StreamHandler())

    try:
        args.func(args)
    except Error as error:
        logger.exception(error)
        sys.exit(str(error))
