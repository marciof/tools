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
import sys
from urllib.parse import parse_qs, urlparse
import webbrowser

# external
import boxsdk
import boxsdk.exception
import dateutil.parser
import onedrivesdk
import onedrivesdk.session
from overrides import overrides

# internal
from cloudsync import client
from cloudsync.error import Error
from cloudsync.state import FileState, PrefixedState

class UnauthenticatedError (Error):
    def __init__(self):
        super().__init__('No authenticated session (did you login?)')

class AuthenticationError (Error):
    def __init__(self):
        super().__init__('Authentication failed')

class Event (metaclass = ABCMeta):

    @abstractmethod
    def apply(self, prefix):
        pass

class CreatedFileEvent (Event):

    def __init__(self, path, access_time, mod_time, write, logger):
        self.path = path
        self.access_time = access_time
        self.mod_time = mod_time
        self.write = write
        self.logger = logger.getChild(self.__class__.__name__)

    @overrides
    def apply(self, prefix):
        path = os.path.join(prefix, self.path)

        self.logger.debug('Create file at %s', path)
        self.write(path)

        self.logger.debug('Set file access and modified times to %s and %s',
            self.access_time, self.mod_time)
        os.utime(path,
            (self.access_time.timestamp(), self.mod_time.timestamp()))

class CreatedFolderEvent (Event):

    def __init__(self, path, access_time, mod_time, logger):
        self.path = path
        self.access_time = access_time
        self.mod_time = mod_time
        self.logger = logger.getChild(self.__class__.__name__)

    @overrides
    def apply(self, prefix):
        path = os.path.join(prefix, self.path)

        self.logger.debug('Create folder at %s', path)
        os.makedirs(path, exist_ok = True)

        self.logger.debug('Set folder access and modified times to %s and %s',
            self.access_time, self.mod_time)
        os.utime(path,
            (self.access_time.timestamp(), self.mod_time.timestamp()))

class DeletedFileEvent (Event):

    def __init__(self, path, logger):
        self.path = path
        self.logger = logger.getChild(self.__class__.__name__)

    @overrides
    def apply(self, prefix):
        path = os.path.join(prefix, self.path)
        self.logger.debug('Delete file at %s', path)
        os.remove(path)

class DeletedFolderEvent (Event):

    def __init__(self, path, logger):
        self.path = path
        self.logger = logger.getChild(self.__class__.__name__)

    @overrides
    def apply(self, prefix):
        path = os.path.join(prefix, self.path)
        self.logger.debug('Delete folder at %s', path)
        os.rmdir(path)

class OneDriveSessionState (onedrivesdk.session.Session):

    @overrides
    def save_session(self, **kwargs):
        state = kwargs['state']
        logger = kwargs['logger']

        logger.debug('Save session at %s', state)

        state.set(['token-type'], self.token_type)
        state.set(['expires-at'], str(int(self._expires_at)))
        state.set(['scopes'], '\n'.join(self.scope))
        state.set(['access-token'], self.access_token, is_private = True)
        state.set(['client-id'], self.client_id)
        state.set(['auth-server-url'], self.auth_server_url)
        state.set(['redirect-uri'], self.redirect_uri)

        if self.refresh_token is not None:
            state.set(['refresh-token'], self.refresh_token, is_private = True)

        if self.client_secret is not None:
            state.set(['client-secret'], self.client_secret)

    @staticmethod
    @overrides
    def load_session(**kwargs):
        state = kwargs['state']
        logger = kwargs['logger']

        logger.debug('Load session at %s', state)
        expires_at = state.get(['expires-at'])

        if expires_at is None:
            logger.warning('Assuming no session, no expires-at state found')
            raise UnauthenticatedError()

        session = OneDriveSessionState(
            token_type = state.get(['token-type']),
            expires_in = '0',
            scope_string = ' '.join(state.get(['scopes']).splitlines()),
            access_token = state.get(['access-token']),
            client_id = state.get(['client-id']),
            auth_server_url = state.get(['auth-server-url']),
            redirect_uri = state.get(['redirect-uri']),
            refresh_token = state.get(['refresh-token']),
            client_secret = state.get(['client-secret']))

        session._expires_at = int(expires_at)
        return session

class OneDriveClient (client.Client):

    @overrides
    def __init__(self,
            state,
            logger,
            client_id = '8eaa14b1-642c-4085-a308-82cdc21e32eb',
            client_secret = None,
            api_base_url = 'https://api.onedrive.com/v1.0/',
            redirect_url = 'https://login.microsoftonline.com/common/oauth2/nativeclient',
            scopes = ('wl.signin', 'wl.offline_access', 'onedrive.readwrite'),
            http_provider = None,
            session_type = OneDriveSessionState):

        if http_provider is None:
            http_provider = onedrivesdk.HttpProvider()

        self.state = state
        self.logger = logger.getChild(self.__class__.__name__)
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
        self.logger.debug('Authenticate from saved session')

        self.auth_provider.load_session(
            state = self.state,
            logger = self.logger)

        try:
            self.auth_provider.refresh_token()
        except Exception as e:
            raise AuthenticationError() from e

    @overrides
    def authenticate_url(self, url):
        self.logger.debug('Authenticate from auth URL %s', url)

        try:
            parsed_url = urlparse(url)
        except ValueError as e:
            raise client.InvalidAuthUrlError(url) from e

        [auth_code] = parse_qs(parsed_url.query).get('code', [None])

        if auth_code is None:
            raise client.MissingAuthCodeUrlError(url)
        elif len(auth_code) > 1:
            raise client.MultipleAuthCodesUrlError(url)

        try:
            self.auth_provider.authenticate(
                auth_code, self.redirect_url, self.client_secret)
        except Exception as e:
            raise Error('Invalid authentication code in URL:', url) from e

        self.auth_provider.save_session(
            state = self.state,
            logger = self.logger)

    # FIXME: persist delta token from last check and at which file for resuming
    # FIXME: retry/backoff mechanisms, https://paperairoplane.net/?p=640
    # FIXME: download progress for bigger files?
    # FIXME: handle network disconnects and timeouts gracefully
    @overrides
    def list_changes(self, delta_token):
        self.logger.debug('List changes with delta token %s', delta_token)
        delta_req = self.client.item(id = 'root').delta(delta_token)

        while delta_req is not None:
            self.logger.debug('Get page of delta changes')
            items = delta_req.get()

            for item in items:
                path = os.path.join(
                    re.sub('^[^:]+:', os.curdir, item.parent_reference.path),
                    item.name)

                if self.is_root_item(item):
                    self.logger.debug('Skip root item with ID %s at %s',
                        item.id, path)
                    continue

                self.logger.debug('Cloud item with ID %s', item.id)
                is_folder = item.folder

                if self.is_package_item(item):
                    is_folder = True
                    self.logger.debug('Handle package of type %s as folder %s',
                        self.get_package_item_type(item), path)

                if item.deleted:
                    if is_folder:
                        yield DeletedFolderEvent(path, self.logger)
                    else:
                        yield DeletedFileEvent(path, self.logger)

                # FIXME: use created datetime as access time?
                mod_time = self.localize_item_last_modified_datetime(item)

                if is_folder:
                    yield CreatedFolderEvent(path,
                        access_time = mod_time,
                        mod_time = mod_time,
                        logger = self.logger)
                else:
                    # FIXME: handle requests.exceptions.ConnectionError
                    yield CreatedFileEvent(path,
                        access_time = mod_time,
                        mod_time = mod_time,
                        write = self.client.item(id = item.id).download,
                        logger = self.logger)

            delta_req = onedrivesdk.ItemDeltaRequest.get_next_page_request(
                items, self.client, options = [])

    @overrides
    def login(self):
        self.logger.debug('Open browser for user login')
        webbrowser.open(self.auth_provider.get_auth_url(self.redirect_url))

    # FIXME: move outside as regular functions
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
class BoxClient (client.Client):

    # FIXME: handle client secret storage
    @overrides
    def __init__(self,
            state,
            logger,
            client_id = None,
            client_secret = None,
            redirect_url = 'https://api.box.com/oauth2'):

        if client_id is None:
            client_id = os.environ['BOX_API_CLIENT_ID']

        if client_secret is None:
            client_secret = os.environ['BOX_API_CLIENT_SECRET']

        self.state = state
        self.logger = logger.getChild(self.__class__.__name__)
        self.client = None
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.cached_oauth = None

    @property
    def oauth(self):
        if self.cached_oauth is None:
            self.cached_oauth = boxsdk.OAuth2(
                client_id = self.client_id,
                client_secret = self.client_secret,
                access_token = self.state.get(['access-token']),
                refresh_token = self.state.get(['refresh-token']),
                store_tokens = self.store_tokens)

        return self.cached_oauth

    @overrides
    def authenticate_session(self):
        self.logger.debug('Authenticate from saved session')

        if self.state.get(['access-token']) is None:
            self.logger.warning('Assuming no session, no access-token state found')
            raise UnauthenticatedError()

        self.client = boxsdk.Client(self.oauth)

        try:
            user = self.client.user(user_id = 'me').get()
        except boxsdk.exception.BoxException as e:
            raise AuthenticationError() from e

        self.logger.debug('Logged in as %s with ID %s',
            user['name'], user['id'])

    @overrides
    def authenticate_url(self, url):
        self.logger.debug('Authenticate from auth URL %s', url)

        try:
            parsed_url = urlparse(url)
        except ValueError as e:
            raise client.InvalidAuthUrlError(url) from e

        [auth_code, *rest] = parse_qs(parsed_url.query).get('code', [None])

        if auth_code is None:
            raise client.MissingAuthCodeUrlError(url)
        elif len(rest) > 1:
            raise client.MultipleAuthCodesUrlError(url)

        [csrf_token, *rest] = parse_qs(parsed_url.query).get('state', [None])

        if csrf_token is None:
            raise Error('No CSRF token found in URL:', url)
        elif len(rest) > 1:
            raise Error('Multiple CSRF tokens found in URL:', url)

        stored_csrf_token = self.state.get(['csrf-token'])

        if csrf_token != stored_csrf_token:
            raise Error('CSRF token mismatch (did you login recently?):',
                csrf_token, 'vs', stored_csrf_token)

        self.oauth.authenticate(auth_code)
        self.state.unset(['csrf-token'])
        self.cached_oauth = None

    # FIXME: filter out non-filesystem events
    @overrides
    def list_changes(self, delta_token):
        if delta_token is None:
            delta_token = '0'

        events = self.client.events().get_events(stream_position = delta_token)
        return events['entries']

    @overrides
    def login(self):
        self.logger.debug('Open browser for user login')

        auth_url, csrf_token = self.oauth.get_authorization_url(
            self.redirect_url)

        self.state.set(['csrf-token'], csrf_token, is_private = True)
        webbrowser.open(auth_url)

    def store_tokens(self, access_token, refresh_token):
        self.state.set(['access-token'], access_token, is_private = True)
        self.state.set(['refresh-token'], refresh_token, is_private = True)

app_name = 'cloud-sync'

syslog_handler = SysLogHandler(address = '/dev/log')
syslog_handler.ident = app_name + ': '

root_logger = logging.getLogger(app_name)
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(syslog_handler)

clients = {
    'box': BoxClient,
    'onedrive': OneDriveClient,
}

def make_client(name):
    state = PrefixedState([name], FileState(app_name, root_logger))
    return clients[name](state, root_logger)

def do_login_command(args):
    client = make_client(args.service)

    if args.auth_url is None:
        client.login()
    else:
        client.authenticate_url(args.auth_url)

# FIXME: initial download vs change list
# FIXME: receive where to download to via command line
# FIXME: prevent overwriting existing files?
# FIXME: sandbox download folder (never modify anything outside of it)
# FIXME: rename to "download"?
def do_start_command(args):
    client = make_client(args.service)
    client.authenticate_session()

    for change in client.list_changes(None):
        change.apply('foobar')

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
        root_logger.addHandler(StreamHandler())

    try:
        args.func(args)
    except KeyboardInterrupt as error:
        root_logger.exception(error)
    except Error as error:
        root_logger.exception(error)
        sys.exit(str(error))
