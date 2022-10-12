#!/bin/sh

set -e -u -x

time rsync --archive --partial --progress --delete --exclude=.dropbox.cache \
    ~/Dropbox \
    "/media/$USER/Backup"