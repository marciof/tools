# Scale UI #

## WM/DE ##

1. Open:` ~/.Xresources`
2. Use: `Xft.dpi: 145`

http://blog.mlindgren.ca/entry/2015/02/21/configuring-dpi-in-lubuntu-slash-lxde/
https://wiki.archlinux.org/index.php/xorg#Display_size_and_DPI

## Firefox ##

1. Open: `about:config`
2. Use: `layout.css.devPixelsPerPx=1.5`

https://wiki.archlinux.org/index.php/HiDPI#Firefox

## Mouse pointer ##

1. Open: `~/.config/lxsession/LXDE/desktop.conf`
2. Use: `iGtk/CursorThemeSize=36`

http://bbs.archbang.org/viewtopic.php?id=4435

# Get sudo rights #

1. $ `su -`
2. $ `adduser USERNAME sudo`

http://askubuntu.com/a/7484/163034 

# Use GRUB in console mode (faster) #

1. Open: `/etc/default/grub`
2. Use: `GRUB_TERMINAL=console`
3. $ `update-grub`

https://wiki.ubuntu.com/HardwareSupportComponentsVideoCardsPoulsbo#Post_installation

# Network sync time #

1. $ `apt-get install ntp`

http://askubuntu.com/a/178977/163034 

# Digital clock format #

`%a %l:%M%P%n%x`

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
