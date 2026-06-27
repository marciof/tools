#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


"""
Automatic Color Scheme for Light/Dark Modes.

---

How to change active/inactive titlebar color:

1. Copy an existing color scheme (`Edit Color Scheme` and `Save As`)
   that has active/inactive titlebar colors.
2. Ensure there aren't any `[Colors:Header]` and `[Colors:Header][Inactive]`
   sections in the new color scheme file.
3. Ensure there is a `[WM]` section in the new color scheme file, which
   will have the active/inactive titlebar colors.

References:

- KDE Plasma docs: https://develop.kde.org/docs/plasma/theme/theme-details/#colors
- KDE bug #433761: https://bugs.kde.org/show_bug.cgi?id=433761
- KDE bug #446584: https://bugs.kde.org/show_bug.cgi?id=446584
- KDE bug #433059: https://bugs.kde.org/show_bug.cgi?id=433059
"""


# FIXME refactor to reduce coupling
# FIXME tests (including mypy)
# FIXME error handling
# FIXME documentation
# FIXME logging
# FIXME typing
# FIXME runs event listener twice when color scheme changes


# standard
import argparse
from enum import Enum
import logging
from logging.handlers import SysLogHandler
import os
import signal
import socket
import subprocess
import sys
import time
from typing import Callable, Dict, List, NoReturn, Optional

# external
from PyQt6.QtCore import pyqtSlot, QObject, QSharedMemory, QSocketNotifier
from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusVariant
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon


class ColorMode (Enum):
    """
    https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html
    """

    NONE = 0
    DARK = 1
    LIGHT = 2


class KdePlasmaAppearance:

    def __init__(self, logger: logging.Logger):
        self._logger = logger


    def apply_color_scheme(self, name: str) -> None | LookupError:
        self._logger.info('KDE Plasma applying color scheme: %s', name)

        plasma_proc = subprocess.run(
            ['plasma-apply-colorscheme', '--', name],
            capture_output=True,
            text=True)

        stdout = plasma_proc.stdout.strip()
        stderr = plasma_proc.stderr.strip()

        self._logger.debug('KDE Plasma exit code: %s', plasma_proc.returncode)
        self._logger.info('KDE Plasma stdout: %s', stdout)
        self._logger.error('KDE Plasma stderr: %s', stderr)

        if plasma_proc.returncode != os.EX_OK:
            raise LookupError(stderr or stdout)


    def list_color_schemes(self) -> str:
        plasma_proc = subprocess.run(
            ['plasma-apply-colorscheme', '--list-schemes'],
            capture_output=True,
            text=True)

        return plasma_proc.stdout.strip()


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
        self._time_interval = 1
        self._last_color_time = 0
        self._on_color_mode_callbacks: List[Callable[[ColorMode], None]] = []
        self._kde_plasma_appearance = KdePlasmaAppearance(logger)

        self._logger.debug('Setting up desktop D-Bus session...')
        self._dbus_session = QDBusConnection.sessionBus()
        self._dbus_session.connect(
            self.DESKTOP_SERVICE,
            self.DESKTOP_PATH,
            self.SETTINGS_INTERFACE,
            'SettingChanged',
            self._filter_on_color_mode_appearance_changes)


    @pyqtSlot(str, str, QDBusVariant)
    def _filter_on_color_mode_appearance_changes(
            self, namespace: str, key: str, value: QDBusVariant) -> None:

        if namespace != self.APPEARANCE_NAMESPACE:
            return
        if key != self.COLOR_SCHEME_KEY:
            return

        if (time.monotonic() - self._last_color_time) < self._time_interval:
            self._logger.info('Ignoring too-quick desktop color mode change')
            return

        self._last_color_time = time.monotonic()

        color_mode_id: int = value.variant()
        color_mode = ColorMode(color_mode_id)
        self._logger.info('Desktop color mode changed: %s', color_mode.name)

        for callback in self._on_color_mode_callbacks:
            callback(color_mode)


    def get_current_color_mode(self) -> ColorMode:
        settings = QDBusInterface(
            self.DESKTOP_SERVICE,
            self.DESKTOP_PATH,
            self.SETTINGS_INTERFACE,
            self._dbus_session)

        response = settings.call(
            'Read', self.APPEARANCE_NAMESPACE, self.COLOR_SCHEME_KEY)

        color_mode_id: int = response.arguments()[0]
        color_mode = ColorMode(color_mode_id)
        self._logger.info('Current desktop color mode: %s', color_mode.name)
        return color_mode


    def on_color_mode(self, callback: Callable[[ColorMode], None]) -> None:
        self._on_color_mode_callbacks.append(callback)


    def apply_color_scheme(self, name: str) -> None | LookupError:
        self._last_color_time = time.monotonic()
        self._kde_plasma_appearance.apply_color_scheme(name)


    def list_color_schemes(self) -> str:
        return self._kde_plasma_appearance.list_color_schemes()


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


class ColorModeTrayIcon (QSystemTrayIcon):

    """
    https://doc.qt.io/qt-6/qicon.html#ThemeIcon-enum
    """
    TRAY_ICON_BY_COLOR_MODE: Dict[ColorMode, QIcon] = {
        ColorMode.LIGHT: QIcon.fromTheme(QIcon.ThemeIcon.WeatherClear),
        ColorMode.DARK: QIcon.fromTheme(QIcon.ThemeIcon.WeatherClearNight),
    }

    def __init__(
            self,
            desktop_appearance: DesktopAppearance,
            logger: logging.Logger):

        super().__init__()
        self._logger = logger

        desktop_appearance.on_color_mode(self._update_icon)
        self._update_icon(desktop_appearance.get_current_color_mode())


    def _update_icon(self, color_mode: ColorMode) -> None:
        icon = self.TRAY_ICON_BY_COLOR_MODE[color_mode]
        self._logger.info(
            'Tray icon update: %s --> %s', color_mode.name, icon.name())
        self.setIcon(icon)


class AutoColorSchemeApp (QApplication):

    APP_NAME: str = 'Auto Color Scheme'


    def __init__(
            self,
            qargs: List[str],
            light: Optional[str] = None,
            dark: Optional[str] = None):

        super().__init__(qargs)

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

        self._sigint_handler = SigIntHandler(self._logger)
        self._sigint_handler.on_signal(self.quit)

        self._shared_instance = self._ensure_single_instance()
        self._desktop_appearance = DesktopAppearance(self._logger)

        if (light, dark) == (None, None):
            self._show_warning_message_box(
                'No color scheme specified.\n\n'
                + self._desktop_appearance.list_color_schemes())
            self.quit()

        self._logger.info('Color schemes: LIGHT=%s, DARK=%s', light, dark)

        self._color_scheme_by_mode: Dict[ColorMode, Optional[str]] = {
            ColorMode.LIGHT: light,
            ColorMode.DARK: dark,
        }

        self._desktop_appearance.on_color_mode(self.apply_color_scheme_by_mode)
        self.apply_color_scheme_by_mode(
            self._desktop_appearance.get_current_color_mode())

        self._menu = QMenu()
        exit_action = QAction('Quit', self._menu)
        exit_action.triggered.connect(self.quit)
        self._menu.addAction(exit_action)

        self._trayIcon = ColorModeTrayIcon(
            self._desktop_appearance, self._logger)
        self._trayIcon.setToolTip(self.APP_NAME)
        self._trayIcon.setContextMenu(self._menu)
        self._trayIcon.show()

        self._logger.info('Running...')


    def _ensure_single_instance(self) -> SharedInstance | NoReturn:
        shared_instance = SharedInstance(
            key='com.marciof.tools.autoColorScheme',
            logger=self._logger)

        if shared_instance.is_shared():
            self._logger.info('Another application instance is already running')
            self._show_warning_message_box('Already running.')
            self.quit()

        return shared_instance


    def _show_warning_message_box(self, text: str) -> None:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(text)
        msg.setWindowTitle(self.APP_NAME)
        msg.exec()


    def quit(self) -> NoReturn:
        self._logger.info('Quitting...')
        super().quit()
        raise SystemExit()


    def apply_color_scheme_by_mode(self, color_mode: ColorMode) -> None:
        color_scheme = self._color_scheme_by_mode[color_mode]

        if color_scheme is None:
            self._logger.info(
                'No color scheme set for mode: %s', color_mode.name)
            return

        self._logger.info(
            'Applying color scheme for mode: %s --> %s',
            color_mode.name,
            color_scheme)

        try:
            self._desktop_appearance.apply_color_scheme(color_scheme)
        except LookupError as error:
            self._show_warning_message_box(str(error))


def main(argv: List[str]) -> NoReturn:
    (description, epilog) = map(str.strip,  __doc__.split('---'))

    arg_parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    arg_parser.add_argument('-l', '--light', help='name of light color scheme')
    arg_parser.add_argument('-d', '--dark', help='name of dark color scheme')

    (parsed_args, unknown_args) = arg_parser.parse_known_args(argv)
    qargs = [argv[0]] + unknown_args

    sys.exit(AutoColorSchemeApp(qargs, **vars(parsed_args)).exec())


if __name__ == '__main__':
    main(sys.argv)
