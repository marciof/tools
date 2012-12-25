#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
import Tkinter
import tkMessageBox
from urllib import urlencode
from urllib2 import urlopen


TITLE = 'Vodafone MBSD'
ADMIN_URL = 'http://VodafoneMobileBroadband.SharingDock'
ADMIN_PASSWORD = 'admin'


Tkinter.Tk().wm_withdraw()

if tkMessageBox.askyesno(TITLE, 'Start rescan?'):
    try:
        urlopen(ADMIN_URL + '/cgi-bin/login.cgi', data = urlencode({
            'AdPassword': ADMIN_PASSWORD,
        }))
        
        urlopen(ADMIN_URL + '/cgi-bin/usb_modem.cgi', data = urlencode({
            'rescan': '1',
        }))
    except BaseException:
        tkMessageBox.showerror(TITLE, 'Rescan error.')
    else:
        tkMessageBox.showinfo(TITLE, 'Rescan started.')
    finally:
        urlopen(ADMIN_URL + '/cgi-bin/logout.cgi', data = urlencode({}))
