#!/usr/bin/env python3

# standard
from argparse import ArgumentParser
import logging
from logging import StreamHandler
from logging.handlers import SysLogHandler
import os
import os.path
import sys
from urllib.parse import parse_qs, urlparse
import webbrowser

# external
import boxsdk
import boxsdk.exception
from overrides import overrides

# internal
from cloudsync import client
from cloudsync.clients import onedrive
from cloudsync.error import Error
from cloudsync.state import FileState, PrefixedState

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
            raise client.UnauthenticatedError()

        self.client = boxsdk.Client(self.oauth)

        try:
            user = self.client.user(user_id = 'me').get()
        except boxsdk.exception.BoxException as e:
            raise client.AuthenticationError() from e

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
    'onedrive': onedrive.OneDriveClient,
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
