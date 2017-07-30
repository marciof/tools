#!/usr/bin/env python3

# standard
from abc import ABCMeta, abstractmethod
from urllib.parse import parse_qs, urlparse
import webbrowser

# external
import appdirs
import onedrivesdk
import onedrivesdk.session
from overrides import overrides

class Sync (metaclass = ABCMeta):
    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def list_changes(self):
        pass

class OneDriveAppDirsSession (onedrivesdk.session.Session):
    @overrides
    def save_session(self, **save_session_kwargs):
        print('save', appdirs.user_cache_dir(appname = 'lsync'))
        return super().save_session(**save_session_kwargs)

    @staticmethod
    @overrides
    def load_session(**load_session_kwargs):
        print('load', appdirs.user_cache_dir(appname = 'lsync'))
        return onedrivesdk.session.Session.load_session(**load_session_kwargs)

class OneDriveSync (Sync):

    def __init__(self,
            client_id = '8eaa14b1-642c-4085-a308-82cdc21e32eb',
            client_secret = None,
            api_base_url = 'https://api.onedrive.com/v1.0/',
            redirect_url = 'https://login.microsoftonline.com/common/oauth2/nativeclient',
            scopes = ('wl.signin', 'wl.offline_access', 'onedrive.readwrite'),
            http_provider = None,
            session_type = OneDriveAppDirsSession):

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

    # FIXME: decouple from session save/load and save in proper folder
    @overrides
    def authenticate(self):
        try:
            self.auth_provider.load_session()
        except FileNotFoundError:
            # FIXME: GUI
            print('Sync needs your permission to access your OneDrive.')
            print('After logging in, copy and paste the final URL here.')
            print('Press ENTER now to open the browser.')
            input()

            # FIXME: handle deny
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
