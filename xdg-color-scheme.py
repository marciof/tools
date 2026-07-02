#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


"""
XDG Color Scheme event listener.

---

See also:

- Yin-Yang: https://github.com/oskarsh/Yin-Yang
- Koi: https://github.com/baduhai/Koi
- auto-knight: https://github.com/DimseBoms/auto-knight
- Blueblack: https://github.com/smitropoulos/blueblack
- darkman: https://gitlab.com/WhyNotHugo/darkman
"""


# standard
import argparse
from enum import IntEnum, unique
import logging
from logging.handlers import SysLogHandler
import signal
import socket
import sys
import time
from typing import Callable, Dict, List, NoReturn

# external
from PyQt6.QtCore import pyqtSlot, QObject, QSharedMemory, QSocketNotifier
from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusVariant
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon


@unique
class ColorScheme (IntEnum):

    """
    https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html
    """

    NONE = 0
    DARK = 1
    LIGHT = 2


    @staticmethod
    def to_name(scheme: int) -> str:
        names: Dict[int, str] = {
            ColorScheme.NONE: 'none',
            ColorScheme.DARK: 'dark',
            ColorScheme.LIGHT: 'light',
        }

        return names.get(scheme, str(scheme))


class DesktopAppearance (QObject):

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
        self._change_rate_time_interval: float = 1
        self._on_color_scheme_timestamp: float = 0
        self._on_color_scheme_callbacks: List[Callable[[int], None]] = []

        self._logger.debug('Setting up desktop D-Bus session...')
        self._dbus_session = QDBusConnection.sessionBus()

        is_connected: bool = self._dbus_session.connect(
            self.DESKTOP_SERVICE,
            self.DESKTOP_PATH,
            self.SETTINGS_INTERFACE,
            'SettingChanged',
            self._filter_on_color_scheme_appearance_changes)

        if not is_connected:
            raise LookupError('Failed to connect to desktop D-Bus session.')


    @pyqtSlot(str, str, QDBusVariant)
    def _filter_on_color_scheme_appearance_changes(
            self, namespace: str, key: str, value: QDBusVariant) -> None:

        if namespace != self.APPEARANCE_NAMESPACE:
            return
        if key != self.COLOR_SCHEME_KEY:
            return

        color_scheme: int = value.variant()
        last_time_interval = (time.monotonic() - self._on_color_scheme_timestamp)

        if last_time_interval < self._change_rate_time_interval:
            self._logger.info('Ignoring too-quick desktop color scheme change')
            return

        self._on_color_scheme_timestamp = time.monotonic()
        self._logger.info(
            'Desktop color scheme changed: %s',
            ColorScheme.to_name(color_scheme))

        for callback in self._on_color_scheme_callbacks:
            callback(color_scheme)


    def get_current_color_scheme(self) -> int:
        settings = QDBusInterface(
            self.DESKTOP_SERVICE,
            self.DESKTOP_PATH,
            self.SETTINGS_INTERFACE,
            self._dbus_session)

        response = settings.call(
            'ReadOne', self.APPEARANCE_NAMESPACE, self.COLOR_SCHEME_KEY)

        color_scheme: int = response.arguments()[0]
        self._logger.info(
            'Current desktop color scheme: %s',
            ColorScheme.to_name(color_scheme))

        return color_scheme


    def on_color_scheme(self, callback: Callable[[int], None]) -> None:
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
            'SIGINT handler socket fds: read=%s write=%s',
            self._read_socket.fileno(),
            self._write_socket.fileno())

        # No-op signal handler, callbacks are used in Qt's event loop instead.
        signal.set_wakeup_fd(self._write_socket.fileno())
        signal.signal(signal.SIGINT, lambda sig, frame: None)

        self._socket_notifier = QSocketNotifier(
            self._read_socket.fileno(), QSocketNotifier.Type.Read, self)
        self._socket_notifier.activated.connect(self._on_signal_received)


    def _on_signal_received(self) -> None:
        self._logger.debug('SIGINT received (Ctrl+C)')

        for callback in self._callbacks:
            callback()


    def on_signal(self, callback: Callable[[], None]) -> None:
        self._callbacks.append(callback)


class ColorSchemeTrayIcon (QSystemTrayIcon):

    """
    https://doc.qt.io/qt-6/qicon.html#ThemeIcon-enum
    """
    COLOR_SCHEME_TO_ICON: Dict[int, QIcon] = {
        ColorScheme.DARK: QIcon.fromTheme(QIcon.ThemeIcon.WeatherClearNight),
        ColorScheme.LIGHT: QIcon.fromTheme(QIcon.ThemeIcon.WeatherClear),
    }

    def __init__(
            self,
            desktop_appearance: DesktopAppearance,
            logger: logging.Logger):

        super().__init__()
        self._logger = logger

        desktop_appearance.on_color_scheme(self._update_icon)
        self._update_icon(desktop_appearance.get_current_color_scheme())


    def _update_icon(self, color_scheme: int) -> None:
        icon = self.COLOR_SCHEME_TO_ICON.get(
            color_scheme, QIcon.fromTheme(QIcon.ThemeIcon.WeatherFog))

        self._logger.info(
            'Tray icon update: %s --> %s',
            ColorScheme.to_name(color_scheme),
            icon.name())

        self.setIcon(icon)


def get_syslog_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    syslog_handler = SysLogHandler(address='/dev/log')
    syslog_handler.setFormatter(logging.Formatter(
        '%(name)s[%(process)d]: %(message)s'))

    logger.addHandler(syslog_handler)
    return logger


class XdgColorSchemeApp (QApplication):

    APP_NAME: str = 'XDG Color Scheme'


    def __init__(self, qargs: List[str], tty: bool = True):
        super().__init__(qargs)
        self._logger = get_syslog_logger(self.__class__.__name__)

        self._sigint_handler = SigIntHandler(self._logger)
        self._sigint_handler.on_signal(self.quit)

        if tty and not sys.stdin.isatty():
            self._show_warning_message_box('No TTY detected.')
            self.quit()

        self._shared_instance = self._ensure_single_instance()
        self._desktop_appearance = DesktopAppearance(self._logger)

        self._desktop_appearance.on_color_scheme(self.print_color_scheme_name)
        self.print_color_scheme_name(
            self._desktop_appearance.get_current_color_scheme())

        self._menu = QMenu()
        exit_action = QAction('Quit', self._menu)
        exit_action.triggered.connect(self.quit)
        self._menu.addAction(exit_action)

        self._trayIcon = ColorSchemeTrayIcon(
            self._desktop_appearance, self._logger)
        self._trayIcon.setToolTip(self.APP_NAME)
        self._trayIcon.setContextMenu(self._menu)
        self._trayIcon.show()

        self._logger.info('Running...')


    def _ensure_single_instance(self) -> SharedInstance | NoReturn:
        shared_instance = SharedInstance(
            key='com.marciof.tools.xdgColorScheme',
            logger=self._logger)

        if shared_instance.is_shared():
            self._logger.info('Another application instance is already running')
            self._show_warning_message_box('Already running.')
            self.quit()

        return shared_instance


    def _show_warning_message_box(self, text: str) -> None:
        msg = QMessageBox()
        msg.setWindowIcon(QIcon.fromTheme(QIcon.ThemeIcon.VideoDisplay))
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(text)
        msg.setWindowTitle(self.APP_NAME)
        msg.exec()


    def quit(self) -> NoReturn:
        self._logger.info('Quitting...')
        super().quit()
        raise SystemExit()


    def print_color_scheme_name(self, color_scheme: int) -> None:
        name = ColorScheme.to_name(color_scheme)
        self._logger.info('Color scheme: %s', name)
        print(name, flush=True)


def main(argv: List[str]) -> NoReturn:
    (description, epilog) = map(str.strip,  __doc__.split('---'))

    arg_parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    arg_parser.add_argument(
        '-t', '--tty', help='disable TTY check', action='store_false')

    (parsed_args, unknown_args) = arg_parser.parse_known_args(argv)
    qargs = [argv[0]] + unknown_args

    sys.exit(XdgColorSchemeApp(qargs, **vars(parsed_args)).exec())


if __name__ == '__main__':
    main(sys.argv)
