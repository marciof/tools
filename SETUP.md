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
- [Link Shell Extension](https://schinagl.priv.at/nt/hardlinkshellext/linkshellextension.html) link helper
- [Ventoy](https://www.ventoy.net/) ISO bootable USB drive
- [MSEdgeRedirect](https://github.com/rcmaehl/MSEdgeRedirect) redirect to default browser
- [SharpKeys](https://github.com/randyrants/sharpkeys) key remapping
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

Mouse wheel + `Ctrl` for zoom in/out:

`~/.config/feh/buttons`

    zoom_in C-4
    zoom_out C-5

UI tweaks:

`~/.config/feh/themes`

    feh --image-bg black --scale-down --auto-zoom

## IntelliJ

_(Last checked: v2026.2 build #IU-262.8665.258)_

[Switch](https://youtrack.jetbrains.com/projects/PY/articles/SUPPORT-A-3748/Wayland-native-mode-poor-scrolling-and-rendering-performance) to [Vulkan rendering](https://wiki.openjdk.org/spaces/wakefield/pages/77693134/Pure+Wayland+toolkit+prototype) to reduce keyboard lag and general stuttering (may cause some [rendering glitches](https://youtrack.jetbrains.com/issue/JBR-10321/Graphical-glitching-when-WLToolkit-and-Vulkan-enabled)). Under `Help` and `Edit Custom VM Options`:

    -Dsun.java2d.vulkan=true

## Schnelle Umlaute

Enable [Fcitx5](https://fcitx-im.org/wiki/Using_Fcitx_5_on_Wayland#KDE_Plasma) under KDE/Plasma and Wayland:

1. Disable `im-config`:
    ```
    im-config -n none
    ```
2. Disable setting `*_IM_MODULE` variables:
    ```
    mv ~/.config/environment.d/fcitx5.conf{,.bak}
    ```
3. Log out and log in.

## Google Chrome

_(Last checked: v150.0.7871.128)_

To have Duolingo able to use `Ctrl+Space` for replaying audio, set Chrome to use X11:

    google-chrome --ozone-platform=x11

## Wine

For high DPI, in `Wine configuration` (`winecfg`) on the `Graphics` tab, adjust `Screen resolution`.

Alternatively, to just double it:

    (set -x; wine reg query 'HKEY_CURRENT_USER\Control Panel\Desktop' \
    | grep LogPixels \
    | tee /dev/tty \
    | awk '{printf "0x%x\n", strtonum($NF) * 2}' \
    | tee /dev/tty \
    | xargs wine reg add 'HKEY_CURRENT_USER\Control Panel\Desktop' /v LogPixels /t REG_DWORD /f /d)

## Java

For high DPI, double [Java 2D UI scaling](https://docs.oracle.com/en/java/javase/25/troubleshoot/java-2d-properties.html):

    J2D_UISCALE=2

## VLC

Show media time duration in the [window title](https://wiki.videolan.org/Documentation:Format_String/):

1. Open `Preferences`.
2. Switch to `Show settings` `All`.
3. Open `Input / Codecs`.
4. Set `Change title according to current media` to: `$Z ($D)`

Save screenshots with the media name:

1. Open `Preferences`.
2. Switch to the `Video` tab.
3. Under `Video snapshots` set `Prefix` to: `$Z-`
