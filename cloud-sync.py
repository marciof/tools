#!/usr/bin/env python3

# standard
from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser
import logging
from logging import StreamHandler
from logging.handlers import SysLogHandler
import os
import os.path
import re
import stat
import sys
from urllib.parse import parse_qs, urlparse
import webbrowser

# external
import appdirs
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

class NoFileConfigFound (Error):
    pass

class FileConfig:

    def __init__(self, app_name, folder):
        self.path = os.path.join(
            appdirs.user_config_dir(appname = app_name),
            folder)

    # FIXME: remove execute permission
    # FIXME: race condition between writing and setting permissions
    def set(self, filename, value, is_private = False):
        os.makedirs(self.path, exist_ok = True)
        path = os.path.join(self.path, filename)

        with open(path, 'w') as config:
            print(value, file = config, end = '')

        if is_private:
            os.chmod(path, stat.S_IRWXU)

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

    # FIXME: make instance field, and reuse in the client class
    config = FileConfig(app_name, 'onedrive')

    @overrides
    def save_session(self, **save_session_kwargs):
        logger.debug('Save session')

        self.config.set('token-type', self.token_type)
        self.config.set('expires-at', str(int(self._expires_at)))
        self.config.set('scopes', '\n'.join(self.scope))
        self.config.set('access-token', self.access_token, is_private = True)
        self.config.set('client-id', self.client_id)
        self.config.set('auth-server-url', self.auth_server_url)
        self.config.set('redirect-uri', self.redirect_uri)

        if self.refresh_token is not None:
            self.config.set('refresh-token', self.refresh_token,
                is_private = True)

        if self.client_secret is not None:
            self.config.set('client-secret', self.client_secret)

    @staticmethod
    @overrides
    def load_session(**load_session_kwargs):
        logger.debug('Load session')

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

def get_package_item_type(item):
    return item._prop_dict['package']['type']

def is_package_item(item):
    return 'package' in item._prop_dict

def is_root_item(item):
    return 'root' in item._prop_dict

def localize_item_last_modified_datetime(item):
    return dateutil.parser\
        .parse(item._prop_dict['lastModifiedDateTime'])\
        .astimezone()

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
        logger.debug('Authenticate from saved session')

        self.auth_provider.load_session()
        self.auth_provider.refresh_token()

    @overrides
    def authenticate_url(self, url):
        logger.debug('Authenticate from auth URL %s', url)

        try:
            parsed_url = urlparse(url)
        except ValueError:
            raise Error('Invalid authentication URL:', url)

        auth_code = parse_qs(parsed_url.query).get('code')

        if auth_code is None:
            raise Error('No authentication code found in URL:', url)

        try:
            self.auth_provider.authenticate(
                auth_code, self.redirect_url, self.client_secret)
        except Exception as e:
            raise Error('Invalid authentication code:', e)

        self.auth_provider.save_session()

    # FIXME: persist token from last check and at which file for resume
    # FIXME: retry/backoff mechanisms, https://paperairoplane.net/?p=640
    # FIXME: download progress for bigger files?
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

            if is_root_item(item):
                logger.debug('Skip root item with ID %s at %s',
                    item.id, cloud_path)
                continue

            local_path = os.path.join(folder, cloud_path)
            logger.debug('Cloud item with ID %s', item.id)
            is_folder = item.folder

            if is_package_item(item):
                is_folder = True
                logger.debug('Handle package of type %s as folder %s',
                    get_package_item_type(item), cloud_path)

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

            mtime = localize_item_last_modified_datetime(item)
            logger.debug('Set modified time to %s', mtime)
            os.utime(local_path, (mtime.timestamp(),) * 2)

    @overrides
    def login(self):
        logger.debug('Open browser for user login')
        webbrowser.open(self.auth_provider.get_auth_url(self.redirect_url))

services = {'onedrive': OneDriveClient}

def do_login_command(args):
    client = services[args.service]()

    if args.auth_url is None:
        client.login()
    else:
        client.authenticate_url(args.auth_url)

# FIXME: receive where to download to via command line
# FIXME: prevent overwriting existing files?
def do_start_command(args):
    client = services[args.service]()
    client.authenticate_session()
    client.download('foobar')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-v', help = 'verbose output', action = 'store_true',
        dest = 'is_verbose')

    command_parser = parser.add_subparsers(dest = 'command')
    command_parser.required = True

    login_parser = command_parser.add_parser('login', help = 'login to service')
    login_parser.add_argument('service', help = 'service', choices = services)
    login_parser.add_argument('auth_url',
        help = 'authentication URL', nargs = '?')
    login_parser.set_defaults(func = do_login_command)

    start_parser = command_parser.add_parser('start', help = 'start sync')
    start_parser.add_argument('service', help = 'service', choices = services)
    start_parser.set_defaults(func = do_start_command)

    args = parser.parse_args()

    if args.is_verbose:
        logger.addHandler(StreamHandler())

    try:
        args.func(args)
    except Error as error:
        sys.exit(str(error))
