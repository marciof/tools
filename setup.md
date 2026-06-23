# Software

## Linux

- [Ubuntu](https://ubuntu.com/download/desktop) OS / [Debian](http://cdimage.debian.org/cdimage/release/current-live/amd64/iso-hybrid/) OS
- [KDE](https://kde.org) desktop environment
- [Tilix](https://gnunn1.github.io/tilix-web/) tiling terminal
- [Liferea](https://lzone.de/liferea/) feed reader
- [VeraCrypt](https://www.veracrypt.fr) disk encryption
- [KeePassXC](https://keepassxc.org) password manager
- [Solaar](https://pwr-solaar.github.io/Solaar/) Logitech Unifying Receiver manager
- [Qalculate](https://qalculate.github.io) desktop calculator
- [Easy Effects](https://github.com/wwmm/easyeffects) audio equalizer
- [Elisa](https://apps.kde.org/elisa) music/radio player ([KEXP](https://www.kexp.org/streaming-urls) & [logo](https://www.kexp.org/static/assets/img/logo-footer.svg), [C89.5](https://www.c895.org/mp3) & [logo](https://www.c895.org/wp-content/uploads/2024/07/Cling_PurpleBack_WhiteLogo-Update.png))
- [Shortwave](https://apps.gnome.org/Shortwave) internet radio player
- [Blanket](https://apps.gnome.org/Blanket) ambient sounds
- [KDE Connect](https://kdeconnect.kde.org) device pairing
- [Handbrake](https://handbrake.fr) video transcoder
- [LosslessCut](https://github.com/mifi/lossless-cut) video splitting
- [Shotcut](https://www.shotcut.org) video editing/joining
- [Rygel](https://gnome.pages.gitlab.gnome.org/rygel/) home media sharing
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
- [7-Zip](https://www.7-zip.org) archive manager
- [PowerToys](https://github.com/microsoft/PowerToys) Windows utilities
- [AltDrag](https://stefansundin.github.io/altdrag/) window moving tools
- [Ventoy](https://www.ventoy.net/) ISO bootable USB drive
- [MSEdgeRedirect](https://github.com/rcmaehl/MSEdgeRedirect) redirect to default browser
- [KeyzPal](https://github.com/limbo666/KeyzPal) tray Caps Lock indicator
- [Notepad2](https://www.flos-freeware.ch/notepad2.html) simple text editor with syntax highlighting

# Configuration

## GRUB

If [GRUB (as of v2.06)](https://savannah.gnu.org/bugs/index.php?61190) `gfxmode` is set to `gfxterm`, then the keyboard input will have a very noticeable lag the higher the resolution is. Set its terminal output to console to disable graphics mode and remove input lag:

`/etc/default/grub.d/custom.cfg`

    # Fix keyboard input lag on high DPI graphics mode.
    GRUB_TERMINAL_OUTPUT=console

    GRUB_TIMEOUT_STYLE=countdown
    GRUB_TIMEOUT=3

    # Potential workaround for Nvidia GPU freeze.
    GRUB_CMDLINE_LINUX_DEFAULT="$GRUB_CMDLINE_LINUX_DEFAULT nvidia.NVreg_EnableGpuFirmware=0"

And then update the configuration:

    update-grub

## IntelliJ

[Switch to the X11 toolkit](https://youtrack.jetbrains.com/projects/PY/articles/SUPPORT-A-3748/Wayland-native-mode-poor-scrolling-and-rendering-performance) to reduce keyboard lag and general stuttering. Under `Help` and `Edit Custom VM Options`:

    -Dawt.toolkit.name=XToolkit

## Chrome

To enable [Fcitx5](https://fcitx-im.org/wiki/Using_Fcitx_5_on_Wayland#KDE_Plasma) and have Schnelle Umlaute working, disable `im-config`:

    im-config -n none

And force X11:

    google-chrome --ozone-platform=x11

To enable the Gemini sidebar, [enable `glic`](chrome://flags/#glic).

## Wine

In `Wine configuration` (`winecfg`) on the `Graphics` tab, adjust `Screen resolution`.

Alternatively, to double it from `96` to `192` DPI:

    wine reg add 'HKEY_CURRENT_USER\Control Panel\Desktop' /v LogPixels /t REG_DWORD /d 0xC0 /f

## JDownloader

[Official instructions](https://support.jdownloader.org/en/knowledgebase/article/high-dpi-support) for high DPI don't seem to work, so double the [Java 2D UI scaling](https://docs.oracle.com/en/java/javase/25/troubleshoot/java-2d-properties.html) instead.

Options for Flatpak applications:

- Either use [Flatseal](https://github.com/tchx84/flatseal) to set an environment variable: `J2D_UISCALE=2`
- Or use the CLI: `flatpak override --user --env=J2D_UISCALE=2 org.jdownloader.JDownloader`

For non-Flatpak:

- Edit its `.desktop` file (eg. via its menu entry) and in `Exec` prepend with: `env J2D_UISCALE=2 ...`

## Tivoli Orb (Sphera)

For Bluetooth auto-connect, open *Session and Startup* settings:

- *Application Autostart* tab.
- *Add application* button.


    bash -c 'sleep 3 && bluetoothctl connect CC:90:93:09:FF:26'
