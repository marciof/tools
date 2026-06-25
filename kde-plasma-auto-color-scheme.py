#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# FIXME documentation
# FIXME error handling
# FIXME tests
# FIXME logging
# FIXME typing

# standard
from enum import Enum
import logging
from logging.handlers import SysLogHandler
import sys
from typing import Dict, List

# external
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusVariant
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon


DESKTOP_SERVICE: str = 'org.freedesktop.portal.Desktop'
DESKTOP_PATH: str = '/org/freedesktop/portal/desktop'

"""
https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html
"""
SETTINGS_INTERFACE: str = 'org.freedesktop.portal.Settings'

APPEARANCE_NAMESPACE: str = 'org.freedesktop.appearance'
COLOR_SCHEME_KEY: str = 'color-scheme'


class ColorScheme (Enum):
    """
    https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html
    """

    NONE = 0
    DARK = 1
    LIGHT = 2


class AutoColorScheme (QApplication):

    """
    https://doc.qt.io/qt-6/qicon.html#ThemeIcon-enum
    """
    TRAY_ICON_BY_COLOR_SCHEME: Dict[ColorScheme, QIcon] = {
        ColorScheme.DARK: QIcon.fromTheme(QIcon.ThemeIcon.WeatherClearNight),
        ColorScheme.LIGHT: QIcon.fromTheme(QIcon.ThemeIcon.WeatherClear),
    }

    def __init__(self, args: List[str]):
        super().__init__(args)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.addHandler(SysLogHandler(address='/dev/log'))

        self.dbus_session = QDBusConnection.sessionBus()
        self.setQuitOnLastWindowClosed(False)

        self.menu = QMenu()
        exit_action = QAction('Quit', self.menu)
        exit_action.triggered.connect(QApplication.quit)
        self.menu.addAction(exit_action)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.get_current_day_night_cycle_icon())
        self.tray.setToolTip('Auto Color Scheme')
        self.tray.setContextMenu(self.menu)
        self.tray.show()

        self.dbus_session.connect(
            DESKTOP_SERVICE,
            DESKTOP_PATH,
            SETTINGS_INTERFACE,
            'SettingChanged',
            self.on_setting_changed)

        self.logger.info('Running...')


    def get_current_color_scheme(self) -> ColorScheme:
        settings = QDBusInterface(
            DESKTOP_SERVICE,
            DESKTOP_PATH,
            SETTINGS_INTERFACE,
            self.dbus_session)

        response = settings.call(
            'Read', APPEARANCE_NAMESPACE, COLOR_SCHEME_KEY)

        color_scheme_id: int = response.arguments()[0]
        color_scheme = ColorScheme(color_scheme_id)
        self.logger.info('Current color scheme: %s', color_scheme.name)
        return color_scheme


    def get_day_night_cycle_icon(self, color_scheme: ColorScheme) -> QIcon:
        return self.TRAY_ICON_BY_COLOR_SCHEME[color_scheme]


    def get_current_day_night_cycle_icon(self) -> QIcon:
        return self.get_day_night_cycle_icon(self.get_current_color_scheme())


    @pyqtSlot(str, str, QDBusVariant)
    def on_setting_changed(
            self, namespace: str, key: str, value: QDBusVariant) -> None:

        if (namespace, key) != (APPEARANCE_NAMESPACE, COLOR_SCHEME_KEY):
            return

        self.logger.info('Color scheme setting changed: %s', value)

        color_scheme_id: int = value.variant()
        color_scheme = ColorScheme(color_scheme_id)

        self.logger.info('New color scheme: %s', color_scheme.name)
        self.tray.setIcon(self.get_day_night_cycle_icon(color_scheme))

        self.apply_custom_color_scheme()


    def apply_custom_color_scheme(self) -> None:
        pass


if __name__ == '__main__':
    sys.exit(AutoColorScheme(sys.argv).exec())
