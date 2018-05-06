# Install

- [Current live CD + non-free](http://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current-live/amd64/iso-hybrid/)
- [Firmware](https://wiki.debian.org/Firmware)
- [Wifi firmware package](https://packages.debian.org/stretch/all/firmware-iwlwifi/download
)

# Sudo

    su -
    usermod -aG sudo,adm marcio

# High DPI

Appearance: Xfce + Numix (color style, icons, window style)

    apt install numix-gtk-theme numix-icon-theme

Menu editor: `menulibre`

    apt install menulibre

## WM/DE ##

`/usr/share/lightdm/lightdm.conf.d/02_hidpi.conf`

    [Seat:*]
    xserver-command=X -core -dpi 145
    greeter-hide-users=false

`/usr/share/lightdm/lightdm-gtk-greeter.conf.d/02_hidpi.conf`

    [greeter]
    xft-dpi=145

## Qt4 ##

Change font size:

    apt install qt4-qtconfig
    qtconfig

## Gtk ##

Logout and login to apply:

    xfconf-query --create -c xsettings -t string -p /Gtk/IconSizes -s gtk-button=32,32

## Xfce ##

    xfconf-query --create -c xsettings -t int -p /Xft/DPI -s 145

# Mouse speed

    apt install xinput

`~/.xsessionrc`

    xinput set-prop 'pointer:Logitech MX Master' 'libinput Accel Speed' 1

Run `./dbus-xsessionrc.sh` at login.

# PC speaker

`~/.gtkrc-2.0`

    gtk-error-bell = 0

# Digital clock format

    %-l:%M%P %a %-m/%-e

# Login screen background

`/etc/lightdm/lightdm-gtk-greeter.conf`

    [greeter]
    background=COLOR-OR-PATH-TO-IMAGE-FILE
