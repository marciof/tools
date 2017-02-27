# sudo rights #

    su
    adduser USERNAME sudo

# Wifi firmware #

https://packages.debian.org/stretch/all/firmware-iwlwifi/download

# High DPI scaling #

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

# Apt repositories #

In `/etc/apt/sources.list`:

    deb http://httpredir.debian.org/debian stretch contrib main non-free
    deb-src http://httpredir.debian.org/debian stretch contrib main non-free
    deb http://security.debian.org/debian-security/ stretch/updates main contrib non-free
    deb-src http://security.debian.org/debian-security/ stretch/updates main contrib non-free

# Network sync time #

    apt-get install ntp

# Digital clock format #

    %a %l:%M%P%n%x

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
