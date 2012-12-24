#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
from urllib import urlencode
from urllib2 import urlopen


ADMIN_URL = 'http://VodafoneMobileBroadband.SharingDock'
ADMIN_PASSWORD = 'admin'


try:
    urlopen(ADMIN_URL + '/cgi-bin/login.cgi', data = urlencode({
        'AdPassword': ADMIN_PASSWORD,
    }))
    
    urlopen(ADMIN_URL + '/cgi-bin/usb_modem.cgi', data = urlencode({
        'rescan': '1',
    }))
finally:
    urlopen(ADMIN_URL + '/cgi-bin/logout.cgi', data = urlencode({}))
