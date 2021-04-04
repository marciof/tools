# Software

- [Debian](https://www.debian.org) OS
- [Xfce](https://xfce.org) desktop environment
- [Fira Code](https://github.com/tonsky/FiraCode) font
- [Firefox](https://www.firefox.com) browser ([extensions](https://addons.mozilla.org/en-US/firefox/collections/13173821/essentials/))
- [Tor Browser](https://www.torproject.org)
- [MenuLibre](https://bluesabre.org/projects/menulibre/) menu editor
- [VeraCrypt](https://www.veracrypt.fr) disk encryption
- [KeePassXC](https://keepassxc.org) password manager
- [ClipIt](https://github.com/CristianHenzel/ClipIt) clipboard manager
- [Solaar](https://pwr-solaar.github.io/Solaar/) Logitech Unifying Receiver manager
- [KDocker](https://github.com/user-none/KDocker) system tray application docker
- [Signal](https://www.signal.org/) instant messaging
- [Rhythmbox](https://wiki.gnome.org/Apps/Rhythmbox/) music/radio player
- [Spotify](https://www.spotify.com) music streaming
- [Handbrake](https://handbrake.fr) video transcoder
- [Redshift](https://github.com/jonls/redshift) screen color temperature
- [Xournal](http://xournal.sourceforge.net) PDF editor
- [Evince](https://wiki.gnome.org/Apps/Evince) PDF viewer
- [Poppler](https://poppler.freedesktop.org) PDF utilities

# Configuration

## Install

- [Current live CD + non-free](http://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current-live/amd64/iso-hybrid/)
- [Wifi firmware package](https://packages.debian.org/buster/all/firmware-iwlwifi/download)
- [Firmware wiki](https://wiki.debian.org/Firmware)

Surface Book 3:

- [Xubuntu >= 20.10](https://xubuntu.org/download/) (Debian as of v10.9 has less support.)
- Third-party drivers:
  - Don't install [third-party drivers during OS installation as it can sometimes break](https://bugs.launchpad.net/ubuntu-cdimage/+bug/1871268).
  - Install third-party drivers post OS installation: `sudo apt install ubuntu-restricted-extras`
- [Surface specific kernel and setup](https://github.com/linux-surface/linux-surface/wiki/Installation-and-Setup#debian--ubuntu).
- [Surface Book 3 specific setup](https://github.com/linux-surface/linux-surface/wiki/Surface-Book-3).

### Sudo rights

    su -
    adduser marcio sudo
    adduser marcio adm

Surface Book 3: not needed under Xubuntu (?)

## High DPI

    apt install numix-gtk-theme numix-icon-theme

Appearance:

- Style: Adwaita-dark (Numix has light colors)
- Icons: Numix
- Settings: Window Scaling 2x

Window Manager:

- Style: Greybird-dark-accessibility (Numix crops the title bar)

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

    xinput set-prop 'pointer:Logitech MX Vertical' 'libinput Accel Speed' 1

Re-apply it on session changes through D-Bus.

## Keyboard

## Keyboard compose key

*Keyboard*:
- *Layout* tab.
- *Compose key* dropdown.

## Keyboard shortcuts

- `exo-open --launch FileManager`: Alt-E
- `exo-open --launch TerminalEmulator`: Alt-T
- `exo-open --launch WebBrowser`: Alt-W
- `keepassxc`: Alt-K
- `xfce4-popup-whiskermenu`: Alt-M
- `xflock4`: Alt-L
- `xscreensaver-command -activate`: Alt-S
- ClipIt history: Alt-C

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

    screen -d -m script -q -c clipit

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

### Light Locker

Workaround for bug ["This session is locked, you'll be redirected to the unlock
dialog in a few seconds."](https://github.com/the-cavalry/light-locker/issues/126):

1. [Disable Light Locker](https://askubuntu.com/questions/544818/how-do-i-disable-automatic-screen-locking-in-xubuntu#544824) (not removing since it seems to be part of Xfce4?)
   - In *Session and Startup*, *Application Autostart*, disable *Screen Locker*.
   - `killall light-locker`
2. `apt install xscreensaver`
3. In *Power Manager*, *Display*, disable *Handle display power management*.
4. In *Screensaver*:
   - *Display Modes*, enable *Lock Screen After* 0 minutes.
   - *Advanced*, enable *Display Power Management*.

Reboot and re-apply High DPI settings if needed.
