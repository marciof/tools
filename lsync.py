#!/usr/bin/env python3

# standard
from abc import ABCMeta, abstractmethod
import os
import os.path
from urllib.parse import parse_qs, urlparse
import webbrowser

# external
import appdirs
import onedrivesdk
import onedrivesdk.session
from overrides import overrides

class NoFileConfigFound (Exception):
    pass

class FileConfig:

    def __init__(self, folder):
        self.path = os.path.join(
            appdirs.user_config_dir(appname = 'lsync'),
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

class Sync (metaclass = ABCMeta):
    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def list_changes(self):
        pass

class OneDriveFileConfigSession (onedrivesdk.session.Session):

    config = FileConfig('onedrive')

    @overrides
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @overrides
    def save_session(self, **save_session_kwargs):
        print('save')

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
        print('load')

        config = OneDriveFileConfigSession.config
        expires_at = config.get('expires-at')

        if expires_at is None:
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

class OneDriveSync (Sync):

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
    def authenticate(self):
        try:
            self.auth_provider.load_session()
        except NoFileConfigFound:
            # FIXME: GUI
            print('Sync needs your permission to access your OneDrive.')
            print("After logging in, you'll get to a blank page. Copy the URL and paste here.")
            print('Press ENTER now to open the browser.')
            input()

            # FIXME: handle deny
            # FIXME: Opera debug output?
            webbrowser.open(self.auth_provider.get_auth_url(self.redirect_url))
            auth_url = input('Paste the final URL here and then press ENTER: ')

            # FIXME: handle parser errors
            auth_code = parse_qs(urlparse(auth_url).query)['code']

            self.auth_provider.authenticate(
                auth_code, self.redirect_url, self.client_secret)
            self.auth_provider.save_session()
        else:
            # FIXME: how often to refresh?
            self.auth_provider.refresh_token()

    @overrides
    def list_changes(self):
        # FIXME: use logging (syslog?)
        print('Checking for changes')

        # FIXME: persist token from last check
        token = None

        collection_page = self.client.item(id = 'root').delta(token).get()

        for item in collection_page:
            print('-', item.name, item.parent_reference.path)

        print('#', collection_page.token)
        print('#', collection_page.next_page_link)
        print('#', collection_page.delta_link)

if __name__ == "__main__":
    sync = OneDriveSync()
    sync.authenticate()
    sync.list_changes()

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
