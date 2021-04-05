#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Automatically sets feed subscriptions to have their enclosures downloaded.

Development/Testing:

- Tutorial: https://lzone.de/liferea/blog/Writing-Liferea-Plugins-Tutorial-Part-1
- Plugins: https://github.com/lwindolf/liferea/tree/master/plugins
- Symlink this folder to `~/.local/share/liferea/plugins/`.
"""

# external
from gi.repository import GObject, Peas, PeasGtk, Gtk, Liferea, Gdk


class FeedPresetDownloadPlugin (GObject.Object, Liferea.ShellActivatable):
    __gtype_name__ = 'FeedPresetDownloadPlugin'

    object = GObject.property(type = GObject.Object)
    shell = GObject.property(type = Liferea.Shell)

    def do_activate(self):
        print('Hello world!')

    def do_deactivate(self):
        print('Goodbye cruel world...')
