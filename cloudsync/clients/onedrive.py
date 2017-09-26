# standard
import os.path
import re
from urllib.parse import parse_qs, urlparse
import webbrowser

# external
import dateutil.parser
import onedrivesdk
import onedrivesdk.session
from overrides import overrides

# internal
from .. import client, error, event

# FIXME: persist at which file listing changes was (check hash?) for resuming
# FIXME: retry/backoff mechanisms, https://paperairoplane.net/?p=640
# FIXME: download progress for bigger files?
# FIXME: handle requests.exceptions.ConnectionError, never give up just sleep?
# FIXME: handle onedrivesdk.error.OneDriveError unauthenticated (?)
# FIXME: more correct to use a write/change file event, rather than create?
# FIXME: receive delta token as a param for list changes?

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
            raise client.UnauthenticatedError()

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
            raise client.AuthenticationError() from e

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
            raise error.Error('Invalid authentication code in URL:', url) from e

        self.auth_provider.save_session(
            state = self.state,
            logger = self.logger)

    @overrides
    def list_changes(self):
        delta_token = self.state.get(['delta-token'])
        self.logger.debug('List changes with delta token %s', delta_token)
        delta_req = self.client.item(id = 'root').delta(delta_token)

        while delta_req is not None:
            self.logger.debug('Get page of delta changes')
            items = delta_req.get()

            for item in items:
                path = self.get_cloud_item_path(item)

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
                        yield event.DeletedFolderEvent(path, self.logger)
                    else:
                        yield event.DeletedFileEvent(path, self.logger)

                created_time = self.localize_item_created_datetime(item)
                mod_time = self.localize_item_last_modified_datetime(item)

                if is_folder:
                    yield event.CreatedFolderEvent(path,
                        access_time = created_time,
                        mod_time = mod_time,
                        logger = self.logger)
                else:
                    yield event.CreatedFileEvent(path,
                        size = item.size,
                        access_time = created_time,
                        mod_time = mod_time,
                        write = self.client.item(id = item.id).download,
                        logger = self.logger)

            self.state.set(['delta-token'], items.token)
            delta_req = onedrivesdk.ItemDeltaRequest.get_next_page_request(
                items, self.client, options = [])

    @overrides
    def login(self):
        self.logger.debug('Open browser for user login')
        webbrowser.open(self.auth_provider.get_auth_url(self.redirect_url))

    def get_cloud_item_path(self, item):
        # The human-readable path comes after the first colon character.
        # https://dev.onedrive.com/resources/itemReference.htm#remarks

        return os.path.join(
            re.sub('^[^:]+:', os.curdir, item.parent_reference.path),
            item.name)

    def get_package_item_type(self, item):
        return item._prop_dict['package']['type']

    def is_package_item(self, item):
        return 'package' in item._prop_dict

    def is_root_item(self, item):
        return 'root' in item._prop_dict

    def localize_item_created_datetime(self, item):
        return dateutil.parser.parse(item._prop_dict['createdDateTime']) \
            .astimezone()

    def localize_item_last_modified_datetime(self, item):
        return dateutil.parser.parse(item._prop_dict['lastModifiedDateTime']) \
            .astimezone()
