# Software

- [Debian](https://www.debian.org) OS
- [Xfce](https://xfce.org) desktop environment
- [Fira Code](https://github.com/tonsky/FiraCode) font
- [Firefox](https://www.firefox.com) browser
- [MenuLibre](https://bluesabre.org/projects/menulibre/) menu editor
- [VeraCrypt](https://www.veracrypt.fr) disk encryption
- [KeePassXC](https://keepassxc.org) password manager
- [Spotify](https://www.spotify.com) music streaming
- [Xournal](http://xournal.sourceforge.net) PDF editor
- [Evince](https://wiki.gnome.org/Apps/Evince) PDF viewer
- [Solaar](https://pwr-solaar.github.io/Solaar/) Logitech Unifying Receiver manager

# Configuration

## Install

- [Current live CD + non-free](http://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current-live/amd64/iso-hybrid/)
- [Firmware](https://wiki.debian.org/Firmware)
- [Wifi firmware package](https://packages.debian.org/stretch/all/firmware-iwlwifi/download)

### Sudo rights

    su -
    adduser marcio sudo
    adduser marcio adm

## High DPI

Appearance: Xfce + Numix (color style, icons, window style)

    apt install numix-gtk-theme numix-icon-theme

### WM/DE

`/usr/share/lightdm/lightdm.conf.d/02_hidpi.conf`

    [Seat:*]
    xserver-command=X -core -dpi 145
    greeter-hide-users=false

`/usr/share/lightdm/lightdm-gtk-greeter.conf.d/02_hidpi.conf`

    [greeter]
    xft-dpi=145

### Qt4

Change font size:

    apt install qt4-qtconfig
    qtconfig

### Gtk

Logout and login to apply:

    xfconf-query --create -c xsettings -t string -p /Gtk/IconSizes -s gtk-button=32,32

### Xfce

    xfconf-query --create -c xsettings -t int -p /Xft/DPI -s 145

### Spotify

    spotify --force-device-scale-factor=1.5

### Mouse

Open *Mouse and Touchpad*, go to *Theme*, and change *Cursor size* to 32.

## Audio

### PC speaker off

`~/.xsessionrc`

    xset -b

### Bluetooth Audio Sink

[Fix *Protocol Not available*:](https://askubuntu.com/a/801669/163034)

    sudo apt-get install pulseaudio-module-bluetooth
    pactl load-module module-bluetooth-discover

## Mouse

### Logitech Unifying Receiver

    apt install solaar

### Pointer speed

    apt install xinput

`~/.xsessionrc`

    xinput set-prop 'pointer:Logitech MX Master' 'libinput Accel Speed' 1

Run `./dbus-xsessionrc.sh` at login.

## Miscellaneous

### Firefox

For faster scrolling disable *smooth scrooling* in *Preferences*.

### Passwords and keys

GUI for Gnome Keyring:

    apt install seahorse

*Session and Startup*:
- Enable *Automatically save session on logout*.
- Add *SSH Key Agent* to *Application Autostart*.
- Enable *Launch GNOME services on startup*.

### Digital clock format

    %-l:%M%P %a %-m/%-e

### Clipboard

    apt install xfce4-clipman xfce4-clipman-plugin

### Login screen background

`/etc/lightdm/lightdm-gtk-greeter.conf`

    [greeter]
    background=COLOR-OR-PATH-TO-IMAGE-FILE

### Profile image

    apt install accountsservice mugshot

### Printer

[Add printer from network.](http://localhost:631)

    apt install task-print-server

### Unattended upgrades

https://wiki.debian.org/UnattendedUpgrades

[Tray notifications:](https://code.guido-berhoerster.org/projects/pk-update-icon/)

    apt install pk-update-icon

### Evince (Document Viewer) zoom level

https://gitlab.gnome.org/GNOME/evince/blob/master/data/org.gnome.Evince.gschema.xml

    gsettings list-recursively org.gnome.Evince
    gsettings set org.gnome.Evince.Default zoom 1.5
    gsettings set org.gnome.Evince.Default sizing-mode free
