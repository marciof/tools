# Software

- [Debian](https://www.debian.org) OS
- [Xfce](https://xfce.org) desktop environment
- [Fira Code](https://github.com/tonsky/FiraCode) font
- [Firefox](https://www.firefox.com) browser ([extensions](https://addons.mozilla.org/en-US/firefox/collections/13173821/essentials/))
- [Tor](https://www.torproject.org) browser
- [Thunderbird](https://www.thunderbird.net) email/calendar
- [MenuLibre](https://bluesabre.org/projects/menulibre/) menu editor
- [VeraCrypt](https://www.veracrypt.fr) disk encryption
- [KeePassXC](https://keepassxc.org) password manager
- [Authy](https://authy.com) two-factor authentication
- [ClipIt](https://github.com/CristianHenzel/ClipIt) clipboard manager
- [Solaar](https://pwr-solaar.github.io/Solaar/) Logitech Unifying Receiver manager
- [KDocker](https://github.com/user-none/KDocker) system tray application docker
- [Signal](https://www.signal.org) instant messaging
- [Rhythmbox](https://wiki.gnome.org/Apps/Rhythmbox/) music/radio player
- [Spotify](https://www.spotify.com) music streaming
- [DroidCam](https://www.dev47apps.com) phone webcam
- [Handbrake](https://handbrake.fr) video transcoder
- [Rygel](https://wiki.gnome.org/Projects/Rygel) home media sharing
- [Redshift](https://github.com/jonls/redshift) screen color temperature
- [Xournal](http://xournal.sourceforge.net) PDF editor
- [Evince](https://wiki.gnome.org/Apps/Evince) PDF viewer
- [Poppler](https://poppler.freedesktop.org) PDF utilities

# Configuration

## Install

- [Current live CD + non-free](http://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current-live/amd64/iso-hybrid/)
- [Wifi firmware package](https://packages.debian.org/buster/all/firmware-iwlwifi/download)
- [Firmware wiki](https://wiki.debian.org/Firmware)

*Surface Book 3*:

- [Xubuntu >= 20.10](https://xubuntu.org/download/) (Debian as of v10.9 has less support.)
  - Third-party drivers:
    - Don't install [third-party drivers during OS installation as it can sometimes break](https://bugs.launchpad.net/ubuntu-cdimage/+bug/1871268).
    - Install third-party drivers post OS installation: `apt install ubuntu-restricted-extras`
- [Surface specific kernel and setup](https://github.com/linux-surface/linux-surface/wiki/Installation-and-Setup#debian--ubuntu).
- [Surface Book 3 specific setup](https://github.com/linux-surface/linux-surface/wiki/Surface-Book-3).
  - Fix reboot freeze: create `/etc/default/grub.d/00_surface.cfg`, with     `GRUB_CMDLINE_LINUX_DEFAULT='quiet splash reboot=pci'`, and then do `update-grub`.

### Sudo rights

    su -
    adduser marcio sudo
    adduser marcio adm

*Surface Book 3*: not needed under Xubuntu (?).

## High DPI

    apt install numix-gtk-theme numix-icon-theme

*Appearance*:

- *Style*: Adwaita-dark (Numix has light colors)
- *Icons*: Numix
- *Settings*: Window Scaling 2x

*Window Manager*:

- *Style*: Greybird-dark-accessibility (Numix crops the title bar)

### GRUB

Decrease resolution to increase font size:

`/etc/default/grub.d/10_high_dpi.cfg`

    GRUB_GFXMODE=640x480

And then do `update-grub`.

### Qt5

https://doc.qt.io/qt-5/highdpi.html

https://wiki.archlinux.org/index.php/HiDPI#Qt_5

`~/.xsessionrc`

    export QT_AUTO_SCREEN_SCALE_FACTOR=0
    export QT_SCALE_FACTOR=2

### Gnome

Using `dconf-editor` change `/org/gnome/desktop/interface/scaling-factor` to `2`.

### Spotify

    spotify --force-device-scale-factor=2

### Mouse

Open *Mouse and Touchpad*, go to *Theme*, and change *Cursor size* to 48.

## Audio

*Surface Book 3*: use PulseEffects for less *"scratchy"* sound:

- Enable `Equalizer`: `apt install lsp-plugins`
- Lower *7.5hKz* a bit and raise *15.0kHz*.
- Enable *Start Service at Login*.

### Bluetooth Audio Sink

[Fix *Protocol Not available*:](https://askubuntu.com/a/801669/163034)

    apt-get install pulseaudio-module-bluetooth
    pactl load-module module-bluetooth-discover

*Surface Book 3*: not needed under Xubuntu (?).

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

### Digital clock format

    %-l:%M%P %a %-m/%-e

### Clipboard

    screen -d -m script -q -c clipit

### Login screen background

`/etc/lightdm/lightdm-gtk-greeter.conf`

    [greeter]
    background=COLOR_OR_PATH_TO_IMAGE_FILE

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
