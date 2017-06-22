# Wifi firmware

https://packages.debian.org/stretch/all/firmware-iwlwifi/download

# High DPI scaling

Appearance: Xfce, Greybird color style, Breeze icons, Breeze window style

## WM/DE ##

`/usr/share/lightdm/lightdm.conf.d/02_custom.conf`:

    [Seat:*]
    xserver-command=X -core -dpi 145
    greeter-hide-users=false

`/usr/share/lightdm/lightdm-gtk-greeter.conf.d/02_custom.conf`:

    [greeter]
    xft-dpi=145

## Firefox ##

`about:config`:

    layout.css.devPixelsPerPx=1.5

## Qt4 ##

Change font size:

    qtconfig

## Gtk ##

Logout and login to apply:

    xfconf-query -c xsettings -p /Gtk/IconSizes -s gtk-button=32,32

## Xfce ##

    xfconf-query -c xsettings -p /Xft/DPI -s 145

# Apt repositories

In `/etc/apt/sources.list`:

    deb http://httpredir.debian.org/debian stretch contrib main non-free
    deb-src http://httpredir.debian.org/debian stretch contrib main non-free
    deb http://security.debian.org/debian-security/ stretch/updates main contrib non-free
    deb-src http://security.debian.org/debian-security/ stretch/updates main contrib non-free

# Firefox

## Flash Bluetooth

    apt install flashplugin-nonfree-extrasound

Or:

    apt install libflashsupport-pulse

## Diagonal scrolling screen tearing

`about:config`:

    layers.acceleration.force-enabled=true

# Opera Flash

1. Download: https://get.adobe.com/flashplayer/
2. Extract all files to: `/usr/lib/pepperflashplugin-nonfree/`

# Digital clock format

    %-l:%M%P %a %-m/%-e

# Mouse speed

`~/.xsessionrc`:

    xinput set-prop 'pointer:Logitech MX Master' 'libinput Accel Speed' 1
