# Software

- [Xubuntu](https://xubuntu.org/download/) OS
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
- [GIMP](https://www.gimp.org) raster image editor
- [Inkscape](https://inkscape.org) vector image editor
- [Ristretto](https://gitlab.xfce.org/apps/ristretto) image viewer
- [gThumb](https://gitlab.gnome.org/GNOME/gthumb/) image organizer
- [EasyEffects](https://github.com/wwmm/easyeffects) audio equalizer (formerly known as PulseEffects)
- [Rhythmbox](https://wiki.gnome.org/Apps/Rhythmbox/) music/radio player
- [Spotify](https://www.spotify.com) music streaming
- [KDE Connect](https://kdeconnect.kde.org) device pairing
- [VLC](https://www.videolan.org/vlc/) video player
- [Handbrake](https://handbrake.fr) video transcoder
- [Rygel](https://wiki.gnome.org/Projects/Rygel) home media sharing
- [Redshift](https://github.com/jonls/redshift) screen color temperature
- [LibreOffice](https://www.libreoffice.org) office suite and PDF editor
- [gscan2pdf](http://gscan2pdf.sourceforge.net) image/scanner with OCR to PDF
- [Evince](https://wiki.gnome.org/Apps/Evince) PDF viewer and forms
- [Poppler](https://poppler.freedesktop.org) PDF utilities
- [Blueman](https://github.com/blueman-project/blueman) bluetooth manager
- [Mousepad](https://github.com/codebrainz/mousepad) simple text editor
- [Mugshot](https://github.com/bluesabre/mugshot) user profile editor
- [LightDM GTK+ Greeter](https://github.com/mjun/lightdm-gtk-greeter-settings) login screen editor

## Windows

- [Auto Dark Mode](https://github.com/AutoDarkMode/Windows-Auto-Night-Mode) theme switch
- [laplock](https://github.com/dechamps/laplock) automatic session lock
- [ProduKey](https://www.nirsoft.net/utils/product_cd_key_viewer.html) key viewer
- [BatteryInfoView](https://www.nirsoft.net/utils/battery_information_view.html) battery level tray icon
- [7-Zip](https://www.7-zip.org) archive manager
- [PowerToys](https://github.com/microsoft/PowerToys) Windows utilities
- [AltDrag](https://stefansundin.github.io/altdrag/) window moving tools
- [Ventoy](https://www.ventoy.net/) ISO bootable USB drive
- [MSEdgeRedirect](https://github.com/rcmaehl/MSEdgeRedirect) redirect to default browser
- [KeyzPal](https://github.com/limbo666/KeyzPal) tray Caps Lock indicator
- [Notepad2](https://www.flos-freeware.ch/notepad2.html) simple text editor with syntax highlighting

# Configuration

## High DPI

    apt install numix-gtk-theme numix-icon-theme

*Appearance*, and *LightDM GTK+ Greeter*:

- *Style*: Greybird-dark
- *Icons*: Numix
- *Fonts*:
  - *Size*: 10
  - *Custom DPI setting*: 150

*Window Manager*:

- *Style*: Greybird-dark

### GRUB

If [GRUB (as of v2.06)](https://savannah.gnu.org/bugs/index.php?61190) `gfxmode` is set to `gfxterm`, then the keyboard input will have very noticeable lag the higher the resolution is. Set its terminal output to console to disable graphics mode and remove input lag:

`/etc/default/grub.d/custom.cfg`

    # Fix keyboard input lag on high DPI graphics mode.
    GRUB_TERMINAL_OUTPUT=console

    GRUB_TIMEOUT_STYLE=countdown
    GRUB_TIMEOUT=1

    # Fix freeze on boot.
    GRUB_CMDLINE_LINUX_DEFAULT="$GRUB_CMDLINE_LINUX_DEFAULT nomodeset"

And then update the configuration:

    update-grub

### Spotify

    spotify --force-device-scale-factor=1.5

### Mouse

Open *Mouse and Touchpad*, go to *Theme*, and change *Cursor size* to 32.

## Touchpad

Open *Mouse and Touchpad*, choose the touchpad *Device*, go to *Touchpad*, and set *Disable touchpad while typing* to `0.1s`.

To [enable touchpad natural scrolling](https://askubuntu.com/a/690513/163034), invert the Synaptics scroll delta.

    synclient | grep ScrollDelta

`/etc/X11/Xsession.d/80synaptics`

    synclient HorizScrollDelta=-VALUE_FROM_ABOVE
    synclient VertScrollDelta=-VALUE_FROM_ABOVE

## Keyboard

### Compose key

*Keyboard* settings:

- *Layout* tab.
- *Compose key* dropdown.

Or alternatively in `~/.xsessionrc`:

    setxkbmap -option compose:caps

And disable caps lock:

`/etc/default/keyboard`

    XKBOPTIONS="ctrl:nocaps"

### Emoji input

*Bus Preferences* settings (command `ibus-setup`):

- *Emoji* tab.
- *Keyboard Shortcuts* section.

## Date / Time

Digital clock format:

    %-l:%M%P %a %-m/%-e

## File manager video thumbnails

https://askubuntu.com/questions/1043976/fix-thunar-doesnt-show-image-video-thumbnails-in-xubuntu-18-04

    apt install tumbler tumbler-plugins-extra ffmpegthumbnailer

## Unattended upgrades

https://help.ubuntu.com/community/AutomaticSecurityUpdates

To force update on battery power (eg. if `on_ac_power` is incorrect)
in `/etc/apt/apt.conf.d/50unattended-upgrades` set:

    Unattended-Upgrade::OnlyOnACPower "false";

Tray notification:

    apt install package-update-indicator
