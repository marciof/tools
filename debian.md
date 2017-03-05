# Wifi firmware #

https://packages.debian.org/stretch/all/firmware-iwlwifi/download

# High DPI scaling #

Appearance: Xfce, Greybird color style, Breeze icons, Breeze window style

## WM/DE ##

In `/usr/share/lightdm/lightdm.conf.d/02_custom.conf`:

    [Seat:*]
    xserver-command=X -core -dpi 145
    greeter-hide-users=false

In `/usr/share/lightdm/lightdm-gtk-greeter.conf.d/02_custom.conf`:

    [greeter]
    xft-dpi=145

## Firefox ##

In `about:config` set:

    layout.css.devPixelsPerPx=1.5

## Qt4 ##

Change font size in:

    qtconfig

## Gtk ##

Logout and login to apply:

    xfconf-query -c xsettings -p /Gtk/IconSizes -s gtk-button=32,32

# Apt repositories #

In `/etc/apt/sources.list`:

    deb http://httpredir.debian.org/debian stretch contrib main non-free
    deb-src http://httpredir.debian.org/debian stretch contrib main non-free
    deb http://security.debian.org/debian-security/ stretch/updates main contrib non-free
    deb-src http://security.debian.org/debian-security/ stretch/updates main contrib non-free

# Digital clock format #

    %-l:%M%P %a %-m/%-e

# Mouse speed #

In `~/.xsessionrc`:

    xinput set-prop 'pointer:Logitech MX Master' 'libinput Accel Speed' 1

# Emacs #

- spacemacs.org
- YASnippet
- Magit
- Restclient
- Multiple-cursors
- Jump to any point in the screen: https://www.youtube.com/watch?v=UZkpmegySnc
- Rainbow mode
- paredit
- @emacsrocks
