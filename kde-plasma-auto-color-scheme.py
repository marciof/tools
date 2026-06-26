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
from typing import Callable, Dict, List, NoReturn

# external
from PyQt6.QtCore import pyqtSlot, QObject, QSharedMemory, QSocketNotifier
from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusVariant
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon


class ColorScheme (Enum):
    """
    https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html
    """

    NONE = 0
    DARK = 1
    LIGHT = 2


class DesktopAppearanceApi (QObject):

    DESKTOP_SERVICE: str = 'org.freedesktop.portal.Desktop'
    DESKTOP_PATH: str = '/org/freedesktop/portal/desktop'

    """
    https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html
    """
    SETTINGS_INTERFACE: str = 'org.freedesktop.portal.Settings'

    APPEARANCE_NAMESPACE: str = 'org.freedesktop.appearance'
    COLOR_SCHEME_KEY: str = 'color-scheme'


    def __init__(self, logger: logging.Logger):
        super().__init__()

        self._logger = logger
        self._on_color_scheme_callbacks: List[Callable[[ColorScheme], None]] = []

        self._logger.debug('Setting up D-Bus session...')
        self._dbus_session = QDBusConnection.sessionBus()
        self._dbus_session.connect(
            self.DESKTOP_SERVICE,
            self.DESKTOP_PATH,
            self.SETTINGS_INTERFACE,
            'SettingChanged',
            self._filter_on_color_scheme_changes)


    @pyqtSlot(str, str, QDBusVariant)
    def _filter_on_color_scheme_changes(
            self, namespace: str, key: str, value: QDBusVariant) -> None:

        if namespace != self.APPEARANCE_NAMESPACE:
            return
        if key != self.COLOR_SCHEME_KEY:
            return

        color_scheme_id: int = value.variant()
        color_scheme = ColorScheme(color_scheme_id)
        self._logger.info('Color scheme setting changed: %s', color_scheme.name)

        for callback in self._on_color_scheme_callbacks:
            callback(color_scheme)


    def get_current_color_scheme(self) -> ColorScheme:
        settings = QDBusInterface(
            self.DESKTOP_SERVICE,
            self.DESKTOP_PATH,
            self.SETTINGS_INTERFACE,
            self._dbus_session)

        response = settings.call(
            'Read', self.APPEARANCE_NAMESPACE, self.COLOR_SCHEME_KEY)

        color_scheme_id: int = response.arguments()[0]
        color_scheme = ColorScheme(color_scheme_id)
        return color_scheme


    def on_color_scheme(self, callback: Callable[[ColorScheme], None]):
        self._on_color_scheme_callbacks.append(callback)


class SharedInstance:

    def __init__(self, key: str, logger: logging.Logger):
        self._logger = logger
        self._shared_memory = QSharedMemory(key)
        self._logger.debug('Shared memory: %s', key)


    def is_shared(self) -> bool:
        return self._shared_memory.attach() or not self._shared_memory.create(1)


class SigIntHandler (QObject):

    def __init__(self, logger: logging.Logger):
        super().__init__()

        self._logger = logger
        self._callbacks: List[Callable[[], None]] = []

        (self._read_socket, self._write_socket) = socket.socketpair()
        self._write_socket.setblocking(False)
        self._read_socket.setblocking(False)

        self._logger.debug(
            'Socket fds for SIGINT handler: read=%s write=%s',
            self._read_socket.fileno(),
            self._write_socket.fileno())

        # No-op signal handler, callbacks are used in Qt's event loop instead.
        signal.set_wakeup_fd(self._write_socket.fileno())
        signal.signal(signal.SIGINT, lambda sig, frame: None)

        self._socket_notifier = QSocketNotifier(
            self._read_socket.fileno(), QSocketNotifier.Type.Read, self)
        self._socket_notifier.activated.connect(self._on_signal_received)


    def _on_signal_received(self) -> None:
        self._logger.debug('Received SIGINT (Ctrl+C)')

        for callback in self._callbacks:
            callback()


    def on_signal(self, callback: Callable[[], None]) -> None:
        self._callbacks.append(callback)


class AutoColorScheme (QApplication):

    APP_NAME: str = 'Auto Color Scheme'

    """
    https://doc.qt.io/qt-6/qicon.html#ThemeIcon-enum
    """
    TRAY_ICON_BY_COLOR_SCHEME: Dict[ColorScheme, QIcon] = {
        ColorScheme.DARK: QIcon.fromTheme(QIcon.ThemeIcon.WeatherClearNight),
        ColorScheme.LIGHT: QIcon.fromTheme(QIcon.ThemeIcon.WeatherClear),
    }


    def __init__(self, args: List[str]):
        super().__init__(args)

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)

        syslog_handler = SysLogHandler(address='/dev/log')
        syslog_handler.setFormatter(logging.Formatter(
            '%(name)s[%(process)d]: %(message)s'))

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(logging.Formatter(
            '%(asctime)s: %(message)s'))

        self._logger.addHandler(stdout_handler)
        self._logger.addHandler(syslog_handler)

        self._shared_instance = self._ensure_single_instance()

        self._sigint_handler = SigIntHandler(self._logger)
        self._sigint_handler.on_signal(self.quit)

        self._desktop_appearance_api = DesktopAppearanceApi(self._logger)

        self._menu = QMenu()
        exit_action = QAction('Quit', self._menu)
        exit_action.triggered.connect(self.quit)
        self._menu.addAction(exit_action)

        self._tray = QSystemTrayIcon()
        self._tray.setIcon(self.get_current_day_night_cycle_icon())
        self._tray.setToolTip(self.APP_NAME)
        self._tray.setContextMenu(self._menu)
        self._tray.show()

        self._desktop_appearance_api.on_color_scheme(
            self.apply_custom_color_scheme)

        self._logger.info('Running...')


    def _ensure_single_instance(self) -> SharedInstance | NoReturn:
        shared_instance = SharedInstance(
            key='com.marciof.tools.kde.plasma.autoColorScheme',
            logger=self._logger)

        if shared_instance.is_shared():
            self._logger.info('Another application instance is already running')

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText('Already running.')
            msg.setWindowTitle(self.APP_NAME)
            msg.exec()

            self.quit()

        return shared_instance


    def quit(self) -> NoReturn:
        self._logger.info('Quitting...')
        super().quit()
        raise SystemExit()


    def get_day_night_cycle_icon(self, color_scheme: ColorScheme) -> QIcon:
        return self.TRAY_ICON_BY_COLOR_SCHEME[color_scheme]


    def get_current_day_night_cycle_icon(self) -> QIcon:
        return self.get_day_night_cycle_icon(
            self._desktop_appearance_api.get_current_color_scheme())


    def apply_custom_color_scheme(self, color_scheme: ColorScheme) -> None:
        self._logger.info('Apply color scheme: %s', color_scheme.name)
        self._tray.setIcon(self.get_day_night_cycle_icon(color_scheme))


if __name__ == '__main__':
    sys.exit(AutoColorScheme(sys.argv).exec())
