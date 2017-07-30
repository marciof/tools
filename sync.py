#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# External
import onedrivesdk

app_id = '8eaa14b1-642c-4085-a308-82cdc21e32eb'
api_base_url = 'https://api.onedrive.com/v1.0/'

# FIXME: first-time auth / access grant
redirect_uri = 'https://login.microsoftonline.com/common/oauth2/nativeclient'

# FIXME: check scopes
scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

http_provider = onedrivesdk.HttpProvider()

auth_provider = onedrivesdk.AuthProvider(
    http_provider = http_provider,
    client_id = app_id,
    scopes = scopes)

client = onedrivesdk.OneDriveClient(api_base_url, auth_provider, http_provider)
print('Authenticating')

# FIXME: save session in proper folder
try:
    auth_provider.load_session()
except FileNotFoundError as e:
    print(auth_provider.get_auth_url(redirect_uri))
    auth_code = input('Paste code here: ')
    auth_provider.authenticate(auth_code, redirect_uri, client_secret = None)
    auth_provider.save_session()
else:
    # FIXME: how often to refresh?
    auth_provider.refresh_token()

# FIXME: use logging (syslog?)
print('Checking for changes')

# FIXME: persist token from last check
token = None

collection_page = client.item(id = 'root').delta(token).get()

for item in collection_page:
    print('-', item.name, item.parent_reference.path)

print('#', collection_page.token)
print('#', collection_page.next_page_link)
print('#', collection_page.delta_link)
