# Scale UI #

http://blog.mlindgren.ca/entry/2015/02/21/configuring-dpi-in-lubuntu-slash-lxde/

1. Open: ~/.Xresources
2. Add: Xft.dpi: 150

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
