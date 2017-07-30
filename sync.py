#!/usr/bin/env python3

# standard
from abc import ABCMeta, abstractmethod
from urllib.parse import parse_qs, urlparse
import webbrowser

# external
import onedrivesdk

class Sync (metaclass = ABCMeta):
    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def list_changes(self):
        pass

class OneDriveSync (Sync):

    def __init__(self):
        # FIXME: make configurable as default arguments
        api_base_url = 'https://api.onedrive.com/v1.0/'
        http_provider = onedrivesdk.HttpProvider()

        # FIXME: check scopes
        self.auth_provider = onedrivesdk.AuthProvider(
            http_provider = http_provider,
            client_id = '8eaa14b1-642c-4085-a308-82cdc21e32eb',
            scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite'])

        self.client = onedrivesdk.OneDriveClient(
            api_base_url, self.auth_provider, http_provider)

    # FIXME: decouple from session save/load and save in proper folder
    def authenticate(self):
        try:
            self.auth_provider.load_session()
        except FileNotFoundError:
            # FIXME: GUI
            print('Sync needs your permission to access your OneDrive.')
            print('After logging in, copy and paste the final URL here.')
            print('Press ENTER now to open the browser.')
            input()

            redirect_url = 'https://login.microsoftonline.com/common/oauth2/nativeclient'
            webbrowser.open(self.auth_provider.get_auth_url(redirect_url))
            auth_url = input('Paste the final URL here and then press ENTER: ')

            # FIXME: handle parser errors
            auth_code = parse_qs(urlparse(auth_url).query)['code']

            self.auth_provider.authenticate(
                auth_code, redirect_url, client_secret = None)
            self.auth_provider.save_session()
        else:
            # FIXME: how often to refresh?
            self.auth_provider.refresh_token()

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
