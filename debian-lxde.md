# Scale UI #

http://blog.mlindgren.ca/entry/2015/02/21/configuring-dpi-in-lubuntu-slash-lxde/
https://wiki.archlinux.org/index.php/xorg#Display_size_and_DPI

1. Open: ~/.Xresources
2. Add: Xft.dpi: 135

# Scale mouse pointer #

http://bbs.archbang.org/viewtopic.php?id=4435

1. Open: ~/.config/lxsession/LXDE/desktop.conf
2. Add line: iGtk/CursorThemeSize=38

# Get sudo rights #

http://askubuntu.com/a/7484/163034 

1. $ adduser USERNAME sudo

# Use GRUB in console mode (faster) #

https://wiki.ubuntu.com/HardwareSupportComponentsVideoCardsPoulsbo#Post_installation

1. Open: /etc/default/grub
2. Add: GRUB_TERMINAL=console
3. $ update-grub

# Network sync time #

http://askubuntu.com/a/178977/163034 

1. $ apt-get install ntp
2. In the Time and Date settings set it to Automatic Update.

# Opera Presto (lightweight, spatial navigation) #

http://arc.opera.com/pub/opera/linux/

1. Add GPG key: wget -O- http://deb.opera.com/archive.key | sudo apt-key add -
1. Download and install.

# Enable Sony Vaio function keys #

@ can change brightness via sysfs
@ can remap Sony function keys
@ ACPI can recognize events

scroll with middle button and pointing stick

$ lsmod | grep gm

http://askubuntu.com/q/624320/163034
https://feeding.cloud.geek.nz/posts/hooking-into-docking-undocking-events-to-run-scripts/
http://askubuntu.com/questions/525995/catch-lid-close-and-open-events
https://wiki.archlinux.org/index.php/acpid

http://forums.fedoraforum.org/showthread.php?t=296958
$ xmodmap -pk | grep -i brightness
WRONG KEYS?

https://ubuntuforums.org/showthread.php?t=88611&page=2
https://github.com/tvogel/vaio-f11-linux/issues/4
https://github.com/dink-straycat/fedora-vpcp

https://wiki.ubuntu.com/Kernel/Debugging/Backlight
https://wiki.archlinux.org/index.php/Intel_GMA_500
https://wiki.archlinux.org/index.php/Backlight

https://bbs.archlinux.org/viewtopic.php?id=138846
$ acpi_listen
$ showkey
$ xev -event keyboard
$ evtest

http://unix.stackexchange.com/questions/89538/how-to-tell-which-keyboard-was-used-to-press-a-key
$ xinput list
$ xinput list-props “Sony Vaio Keys”
$ udevadm info --query=property --name=/dev/input/event4

https://wiki.archlinux.org/index.php/Map_scancodes_to_keycodes
http://unix.stackexchange.com/questions/156985/keyboard-hard-remap-keys
/lib/udev/hwdb.d/60-keyboard.hwdb

/etc/udev/hwdb.d/90-custom-keyboard.hwddb
keyboard:name:Sony Vaio Keys:dmi:bvn*:bvr*:bd*”svnSony*:pnVPC*:pvr*
 KEYBOARD_KEY_0d=a
$ udevadm hwdb --update
$ udevadm trigger

https://hal.freedesktop.org/quirk/quirk-keymap-list.txt

$ ls -l /dev/input/by-path/*-kbd
$ udevadm info --query=property --name=/dev/input/eventX

http://forums.fedoraforum.org/showthread.php?t=296958
http://forums.bodhilinux.com/index.php?/topic/5985-brightness-scripts/#entry56911
$ echo 50 | sudo tee /sys/class/backlight/psb-bl/brightness
$ dmesg | grep sony
"sony_laptop: brightness ignored, must be controlled by ACPI video driver"

https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1054298
$ xrandr -q
$ xrandr --output LVDS-0 --set backlight 50
