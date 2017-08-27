# standard
import os
import os.path
from urllib.parse import parse_qs, urlparse
import webbrowser

# external
import boxsdk
import boxsdk.exception
from overrides import overrides

# internal
from .. import client, error

# FIXME: handle client secret storage, avoid os.environ?
# FIXME: filter out non-filesystem events

class BoxClient (client.Client):

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
            self.logger.warning(
                'Assuming no session, no access-token state found')
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
            raise error.Error('No CSRF token found in URL:', url)
        elif len(rest) > 1:
            raise error.Error('Multiple CSRF tokens found in URL:', url)

        stored_csrf_token = self.state.get(['csrf-token'])

        if csrf_token != stored_csrf_token:
            raise error.Error('CSRF token mismatch (did you login recently?):',
                csrf_token, 'vs', stored_csrf_token)

        self.oauth.authenticate(auth_code)
        self.state.unset(['csrf-token'])
        self.cached_oauth = None

    @overrides
    def list_changes(self):
        events = self.client.events().get_events(stream_position = '0')
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
