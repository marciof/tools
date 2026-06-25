#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
"""

# FIXME refactor to reduce coupling
# FIXME tests (including mypy)
# FIXME error handling
# FIXME documentation
# FIXME logging
# FIXME typing
# FIXME runs event listener twice when color scheme changes

# standard
from enum import Enum
import logging
from logging.handlers import SysLogHandler
import signal
import socket
import sys
from typing import Dict, List, NoReturn

# external
from PyQt6.QtCore import pyqtSlot, QSharedMemory, QSocketNotifier
from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusVariant
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon


APP_NAME: str = 'Auto Color Scheme'

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

        syslog_handler = SysLogHandler(address='/dev/log')
        syslog_handler.setFormatter(logging.Formatter(
            '%(name)s[%(process)d]: %(message)s'))

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(logging.Formatter(
            '%(asctime)s: %(message)s'))

        self.logger.addHandler(stdout_handler)
        self.logger.addHandler(syslog_handler)

        self.shared_memory = self.ensure_single_instance()

        self.logger.debug('Setting up SIGINT handler')
        (self.read_socket, self.write_socket) = socket.socketpair()
        self.write_socket.setblocking(False)
        self.read_socket.setblocking(False)

        # No-op signal handler, quit app in Qt event loop instead.
        signal.set_wakeup_fd(self.write_socket.fileno())
        signal.signal(signal.SIGINT, lambda sig, frame: None)

        self.socket_notifier = QSocketNotifier(
            self.read_socket.fileno(), QSocketNotifier.Type.Read, self)
        self.socket_notifier.activated.connect(self.on_sigint)
        self.logger.debug('Socket fds for SIGINT: read=%s write=%s',
            self.read_socket.fileno(), self.write_socket.fileno())

        self.logger.debug('Setting up D-Bus session')
        self.dbus_session = QDBusConnection.sessionBus()

        self.menu = QMenu()
        exit_action = QAction('Quit', self.menu)
        exit_action.triggered.connect(self.quit)
        self.menu.addAction(exit_action)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.get_current_day_night_cycle_icon())
        self.tray.setToolTip(APP_NAME)
        self.tray.setContextMenu(self.menu)
        self.tray.show()

        self.dbus_session.connect(
            DESKTOP_SERVICE,
            DESKTOP_PATH,
            SETTINGS_INTERFACE,
            'SettingChanged',
            self.on_setting_changed)

        self.logger.info('Running...')


    def ensure_single_instance(self) -> QSharedMemory | SystemExit:
        shared_memory = QSharedMemory(
            'com.marciof.tools.kde.plasma.autoColorScheme')
        self.logger.debug('Created shared memory: %s', shared_memory.key())

        if shared_memory.attach() or not shared_memory.create(1):
            self.logger.info('Another application instance is already running')

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText('Already running.')
            msg.setWindowTitle(APP_NAME)
            msg.exec()

            raise SystemExit()

        return shared_memory


    def quit(self) -> NoReturn:
        self.logger.info('Quitting...')
        super().quit()


    def on_sigint(self) -> None:
        self.logger.debug('Received SIGINT (Ctrl+C)')
        self.socket_notifier.setEnabled(False)
        self.quit()


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

        self.logger.info('Color scheme setting changed')

        color_scheme_id: int = value.variant()
        color_scheme = ColorScheme(color_scheme_id)

        self.logger.info('New color scheme: %s', color_scheme.name)
        self.tray.setIcon(self.get_day_night_cycle_icon(color_scheme))

        self.apply_custom_color_scheme()


    def apply_custom_color_scheme(self) -> None:
        pass


if __name__ == '__main__':
    sys.exit(AutoColorScheme(sys.argv).exec())
