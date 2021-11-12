# Software

- [Xubuntu](https://xubuntu.org/download/) OS ([Debian](http://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current-live/amd64/iso-hybrid/) OS)
- [Xfce](https://xfce.org) desktop environment
- [Synapse](https://launchpad.net/synapse-project) semantic search
- [Fira Code](https://github.com/tonsky/FiraCode) font
- [Vivaldi](https://vivaldi.com) browser ([Firefox extensions](https://addons.mozilla.org/firefox/collections/13173821/essentials/))
- [Tor](https://www.torproject.org) browser
- [Tilix](https://gnunn1.github.io/tilix-web/) tiling terminal
- [Liferea](https://lzone.de/liferea/) feed reader
- [MenuLibre](https://bluesabre.org/projects/menulibre/) menu editor
- [VeraCrypt](https://www.veracrypt.fr) disk encryption
- [KeePassXC](https://keepassxc.org) password manager
- [Xarchiver](https://github.com/ib/xarchiver) archive manager ([Thunar archive plugin](http://users.xfce.org/~benny/projects/thunar-archive-plugin/index.html))
- [Authy](https://authy.com) two-factor authentication
- [Clipman](https://docs.xfce.org/panel-plugins/clipman/start) clipboard manager
- [Solaar](https://pwr-solaar.github.io/Solaar/) Logitech Unifying Receiver manager
- [KDocker](https://github.com/user-none/KDocker) system tray application docker
- [Signal](https://www.signal.org) instant messaging
- [Ristretto](https://gitlab.xfce.org/apps/ristretto) image viewer
- [gThumb](https://gitlab.gnome.org/GNOME/gthumb/) image organizer
- [Rhythmbox](https://wiki.gnome.org/Apps/Rhythmbox/) music/radio player
- [Spotify](https://www.spotify.com) music streaming
- [DroidCam](https://www.dev47apps.com) phone webcam
- [KDE Connect](https://kdeconnect.kde.org) device pairing
- [VLC](https://www.videolan.org/vlc/) video player
- [Handbrake](https://handbrake.fr) video transcoder
- [Rygel](https://wiki.gnome.org/Projects/Rygel) home media sharing
- [uGet](https://ugetdm.com/) download manager
- [Redshift](https://github.com/jonls/redshift) screen color temperature
- [LibreOffice](https://www.libreoffice.org) office suite and PDF editor
- [Evince](https://wiki.gnome.org/Apps/Evince) PDF viewer and forms
- [Poppler](https://poppler.freedesktop.org) PDF utilities
- [Blueman](https://github.com/blueman-project/blueman) bluetooth manager
- [Mousepad](https://github.com/codebrainz/mousepad) simple text editor

## Windows

- [Auto Dark Mode](https://github.com/AutoDarkMode/Windows-Auto-Night-Mode) theme switch
- [laplock](https://github.com/dechamps/laplock) automatic session lock
- [ProduKey](https://www.nirsoft.net/utils/product_cd_key_viewer.html) product key viewer

# Configuration

## Install

### Sudo rights

    su -
    adduser marcio sudo
    adduser marcio adm

*Note*: not needed under Xubuntu (?).

## High DPI

    apt install numix-gtk-theme numix-icon-theme

*Appearance*, and *LightDM GTK+ Greeter*:

- *Style*: Numix
- *Icons*: Numix
- *Fonts*:
  - *Size*: 10
  - *Custom DPI setting*: 150

*Window Manager*:

- *Style*: Numix

### GRUB

Decrease resolution to increase font size:

`/etc/default/grub.d/10_high_dpi.cfg`

    GRUB_GFXMODE=640x480

And then do `update-grub`.

### LightDM Greeter

*Note*: not needed unless using a custom DPI setting.

*Note*: not needed if changed via the *LightDM GTK+ Greeter* UI.

`/usr/share/lightdm/lightdm.conf.d/02_hidpi.conf`

    [Seat:*]
    xserver-command=X -core -dpi 150
    greeter-hide-users=false

`/usr/share/lightdm/lightdm-gtk-greeter.conf.d/02_hidpi.conf`

    [greeter]
    xft-dpi=150

### Qt4

Change font size:

    apt install qt4-qtconfig
    qtconfig

### Qt5

https://doc.qt.io/qt-5/highdpi.html

https://wiki.archlinux.org/index.php/HiDPI#Qt_5

`~/.xsessionrc`

    export QT_AUTO_SCREEN_SCALE_FACTOR=0
    export QT_SCALE_FACTOR=2

### Gtk

*Note*: not needed unless using a custom DPI setting.

    xfconf-query --create -c xsettings -t string -p /Gtk/IconSizes -s gtk-button=32,32

### Xfce

*Note*: not needed unless using a custom DPI setting.

*Note*: not needed if changed via the *Appearance* UI.

    xfconf-query --create -c xsettings -t int -p /Xft/DPI -s 150

### Gnome

Using `dconf-editor` change `/org/gnome/desktop/interface/scaling-factor` to `2`.

### Spotify

    spotify --force-device-scale-factor=1.5

### Mouse

Open *Mouse and Touchpad*, go to *Theme*, and change *Cursor size* to 32.

### Bluetooth Audio Sink

[Fix *Protocol Not available*:](https://askubuntu.com/a/801669/163034)

    apt-get install pulseaudio-module-bluetooth
    pactl load-module module-bluetooth-discover

*Note*: not needed under Xubuntu (?).

## Mouse

### Logitech Unifying Receiver

    apt install solaar

### Touchpad

Open *Mouse and Touchpad*, choose the touchpad *Device*, go to *Touchpad*, and set *Disable touchpad while typing* to `0.1s`.

To [enable touchpad natural scrolling](https://askubuntu.com/a/690513/163034), invert the Synaptics scroll delta.

    synclient | grep ScrollDelta

`/etc/X11/Xsession.d/80synaptics`

    synclient HorizScrollDelta=-VALUE_FROM_ABOVE
    synclient VertScrollDelta=-VALUE_FROM_ABOVE

## Keyboard

## Keyboard compose key

*Keyboard* settings:
- *Layout* tab.
- *Compose key* dropdown.

Or alternatively in `~/.xsessionrc`:

    setxkbmap -option compose:caps

## Miscellaneous

### Passwords and keys

GUI for Gnome Keyring:

    apt install seahorse

*Session and Startup*:
- Enable *Automatically save session on logout*.
- Add *SSH Key Agent* to *Application Autostart*.
- Enable *Launch GNOME services on startup*.

### Date/Time

Automatic timezone:

    apt install ntp

Digital clock format:

    %-l:%M%P %a %-m/%-e

### File manager video thumbnails

https://askubuntu.com/questions/1043976/fix-thunar-doesnt-show-image-video-thumbnails-in-xubuntu-18-04

    apt install tumbler tumbler-plugins-extra ffmpegthumbnailer

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

### Trailing newline

[*Mousepad* may have a bug that hides the trailing newline](https://gitlab.xfce.org/apps/mousepad/-/issues/53). In that case [configure *Gedit* to disable adding trailing newlines](https://askubuntu.com/a/1013115/163034):

    gsettings set org.gnome.gedit.preferences.editor ensure-trailing-newline false

### Redshift startup crashes

1. Remove crash files in `/var/crash`.
2. Disable `systemctl` service: `systemctl --user mask redshift.service redshift-gtk.service`
   - If that doesn't work then rename the files themselves to `*.disabled`: `/usr/lib/systemd/user`
3. Add `redshift-gtk` to *Session and Startup*, under *Application Autostart*.
