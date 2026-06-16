'use strict';

function getProp(service, path, iface, prop, cb) {
    callDBus(
        service,
        path,
        'org.freedesktop.DBus.Properties',
        'Get',
        iface,
        prop,
        cb
    );
}

getProp(
    'org.kde.ScreenBrightness',
    '/org/kde/ScreenBrightness/display0',
    'org.kde.ScreenBrightness.Display',
    'Brightness',
    function (level) {
        print(level);
    }
);

/*
import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction

# Setup App and Tray Icon
app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
tray = QSystemTrayIcon(QIcon.fromTheme("applications-games"))
tray.setVisible(True)

# Context Menu
menu = QMenu()
menu.addAction("Quit", app.quit)
tray.setContextMenu(menu)

sys.exit(app.exec())
 */
