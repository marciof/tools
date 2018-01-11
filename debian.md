# Wifi firmware

https://packages.debian.org/stretch/all/firmware-iwlwifi/download

# High DPI scaling

Appearance: Xfce, Numix color style, Numix window style, Breeze icons

Menu editor: `menulibre`

## WM/DE ##

`/usr/share/lightdm/lightdm.conf.d/02_custom.conf`:

    [Seat:*]
    xserver-command=X -core -dpi 145
    greeter-hide-users=false

`/usr/share/lightdm/lightdm-gtk-greeter.conf.d/02_custom.conf`:

    [greeter]
    xft-dpi=145

## Qt4 ##

Change font size:

    qtconfig

## Gtk ##

Logout and login to apply:

    xfconf-query -c xsettings -p /Gtk/IconSizes -s gtk-button=32,32

## Xfce ##

    xfconf-query -c xsettings -p /Xft/DPI -s 145

# Mouse speed

`~/.xsessionrc`:

    xinput set-prop 'pointer:Logitech MX Master' 'libinput Accel Speed' 1

Run `./dbus-xsessionrc.sh` at login.

# Opera with Flash

1. Download: https://get.adobe.com/flashplayer/
2. Extract all files to: `/usr/lib/pepperflashplugin-nonfree/`

# Digital clock format

    %-l:%M%P %a %-m/%-e

# Login screen background

`/etc/lightdm/lightdm-gtk-greeter.conf`:

    [greeter]
    background=COLOR-OR-PATH-TO-IMAGE-FILE
