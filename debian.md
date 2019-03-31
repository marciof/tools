# Install

- [Current live CD + non-free](http://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current-live/amd64/iso-hybrid/)
- [Firmware](https://wiki.debian.org/Firmware)
- [Wifi firmware package](https://packages.debian.org/stretch/all/firmware-iwlwifi/download)

# Sudo rights

    su -
    adduser marcio sudo
    adduser marcio adm

# High DPI

Appearance: Xfce + Numix (color style, icons, window style)

    apt install numix-gtk-theme numix-icon-theme

Menu editor: `menulibre`

    apt install menulibre

## WM/DE

`/usr/share/lightdm/lightdm.conf.d/02_hidpi.conf`

    [Seat:*]
    xserver-command=X -core -dpi 145
    greeter-hide-users=false

`/usr/share/lightdm/lightdm-gtk-greeter.conf.d/02_hidpi.conf`

    [greeter]
    xft-dpi=145

## Qt4

Change font size:

    apt install qt4-qtconfig
    qtconfig

## Gtk

Logout and login to apply:

    xfconf-query --create -c xsettings -t string -p /Gtk/IconSizes -s gtk-button=32,32

## Xfce

    xfconf-query --create -c xsettings -t int -p /Xft/DPI -s 145

## Spotify

    spotify --force-device-scale-factor=1.5

## Mouse

Open *Mouse and Touchpad*, go to *Theme*, and change *Cursor size* to 32.

# Logitech Unifying Receiver

    apt install solaar

# Mouse speed

    apt install xinput

`~/.xsessionrc`

    xinput set-prop 'pointer:Logitech MX Master' 'libinput Accel Speed' 1

Run `./dbus-xsessionrc.sh` at login.

# Passwords and keys

GUI for Gnome Keyring:

    apt install seahorse

*Session and Startup*:
- Enable *Automatically save session on logout*.
- Add *SSH Key Agent* to *Application Autostart*.
- Enable *Launch GNOME services on startup*.

# PC speaker off

`~/.xsessionrc`

    xset -b

# Digital clock format

    %-l:%M%P %a %-m/%-e

# Login screen background

`/etc/lightdm/lightdm-gtk-greeter.conf`

    [greeter]
    background=COLOR-OR-PATH-TO-IMAGE-FILE

# Profile image

    apt install accountsservice mugshot

# Clipboard

    apt install xfce4-clipman xfce4-clipman-plugin

# Printer

[Add printer from network](http://localhost:631).

    apt install task-print-server

# Unattended upgrades

https://wiki.debian.org/UnattendedUpgrades

# Evince (Document Viewer) zoom level

https://gitlab.gnome.org/GNOME/evince/blob/master/data/org.gnome.Evince.gschema.xml

    gsettings list-recursively org.gnome.Evince
    gsettings set org.gnome.Evince.Default zoom 1.5
    gsettings set org.gnome.Evince.Default sizing-mode free
