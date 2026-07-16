# Software

## Linux

- [Ubuntu](https://ubuntu.com/download/desktop) OS / [Debian](http://cdimage.debian.org/cdimage/release/current-live/amd64/iso-hybrid/) OS
- [KDE](https://kde.org) desktop environment
- [Liferea](https://lzone.de/liferea/) feed reader
- [VeraCrypt](https://www.veracrypt.fr) disk encryption
- [KeePassXC](https://keepassxc.org) password manager
- [Solaar](https://pwr-solaar.github.io/Solaar/) Logitech Unifying Receiver manager
- [Qalculate](https://qalculate.github.io) desktop calculator
- [Easy Effects](https://github.com/wwmm/easyeffects) audio equalizer
- [Shortwave](https://apps.gnome.org/Shortwave) internet radio player
- [Blanket](https://apps.gnome.org/Blanket) ambient sounds
- [KDE Connect](https://kdeconnect.kde.org) device pairing
- [Handbrake](https://handbrake.fr) video transcoder
- [LosslessCut](https://github.com/mifi/lossless-cut) video splitting
- [Shotcut](https://www.shotcut.org) video editing/joining
- [Rygel](https://gnome.pages.gitlab.gnome.org/rygel/) home media sharing
- [feh](https://github.com/derf/feh) fast image viewer
- [Frog](https://tenderowl.com/work/frog/) OCR from images
- [gscan2pdf](http://gscan2pdf.sourceforge.net) image/scanner with OCR to PDF
- [Poppler](https://poppler.freedesktop.org) PDF utilities
- [Blueman](https://github.com/blueman-project/blueman) bluetooth manager
- [Marble](https://marble.kde.org) world atlas map
- [Schnelle Umlaute](https://github.com/Maik-0000FF/schnelle-umlaute/) compose key alternative
- [Flatseal](https://github.com/tchx84/flatseal) Flatpak settings
- [IrScrutinizer](https://github.com/bengtmartensson/IrScrutinizer) IR analysis

## Windows

- [Auto Dark Mode](https://github.com/AutoDarkMode/Windows-Auto-Night-Mode) theme switch
- [laplock](https://github.com/dechamps/laplock) automatic session lock
- [ProduKey](https://www.nirsoft.net/utils/product_cd_key_viewer.html) key viewer
- [BatteryInfoView](https://www.nirsoft.net/utils/battery_information_view.html) battery information
- [Battery Percentage Icon](https://github.com/soleon/Percentage) battery level tray icon
- [Open Hardware Monitor](https://openhardwaremonitor.org) hardware monitor
- [PowerToys](https://github.com/microsoft/PowerToys) utilities
- [AltDrag](https://stefansundin.github.io/altdrag/) window dragging
- [Ventoy](https://www.ventoy.net/) ISO bootable USB drive
- [MSEdgeRedirect](https://github.com/rcmaehl/MSEdgeRedirect) redirect to default browser
- [KeyzPal](https://github.com/limbo666/KeyzPal) tray Caps Lock indicator
- [Notepad2](https://www.flos-freeware.ch/notepad2.html) simple text editor with syntax highlighting
- [Notepad++](https://notepad-plus-plus.org) full-featured text editor

# Configuration

## GRUB

If [GRUB (as of v2.06)](https://savannah.gnu.org/bugs/index.php?61190) `gfxmode` is set to `gfxterm`, then the keyboard input will have a very noticeable lag the higher the resolution is. Set its terminal output to console to disable graphics mode and remove input lag:

`/etc/default/grub.d/custom.cfg`

    # Fix keyboard input lag on high DPI graphics mode.
    GRUB_TERMINAL_OUTPUT=console

    GRUB_TIMEOUT_STYLE=countdown
    GRUB_TIMEOUT=3

And then update the configuration:

    update-grub

## feh

Mouse wheel + Ctrl for zoom in/out:

`~/.config/feh/buttons`

    zoom_in C-4
    zoom_out C-5

UI tweaks:

`~/.config/feh/themes`

    feh --image-bg black --scale-down --auto-zoom

## IntelliJ

[Switch to the X11 toolkit](https://youtrack.jetbrains.com/projects/PY/articles/SUPPORT-A-3748/Wayland-native-mode-poor-scrolling-and-rendering-performance) to reduce keyboard lag and general stuttering. Under `Help` and `Edit Custom VM Options`:

    -Dawt.toolkit.name=XToolkit

## Schnelle Umlaute

To enable [Fcitx5](https://fcitx-im.org/wiki/Using_Fcitx_5_on_Wayland#KDE_Plasma) under KDE/Plasma and Wayland, disable `im-config`:

    im-config -n none

Disable setting `*_IM_MODULE` variables:

    mv ~/.config/environment.d/fcitx5.conf{,.bak}

And then log out and log in.

## Google Chrome

To have Duolingo able to use `Ctrl+Space` for replaying audio, set Chrome to use X11:

    google-chrome --ozone-platform=x11

## Wine

For high DPI, in `Wine configuration` (`winecfg`) on the `Graphics` tab, adjust `Screen resolution`.

Alternatively, to double it from `96` to `192` DPI:

    wine reg add 'HKEY_CURRENT_USER\Control Panel\Desktop' /v LogPixels /t REG_DWORD /d 0xC0 /f

## Java

For high DPI, double the [Java 2D UI scaling](https://docs.oracle.com/en/java/javase/25/troubleshoot/java-2d-properties.html).

Flatpak apps:

- Either use [Flatseal](https://github.com/tchx84/flatseal) to set an environment variable: `J2D_UISCALE=2`
- Or use the CLI: `flatpak override --user --env=J2D_UISCALE=2 com.example.App`

non-Flatpak:

- Edit its `.desktop` file (eg. via its menu entry) and in `Exec` prepend with: `env J2D_UISCALE=2 ...`
