#!/bin/sh

set -e -u -x
date
rsync \
    --archive --partial --delete --executability --atimes --no-links \
    --human-readable --info=progress1,name0 \
    --exclude=.dropbox.cache \
    ~/Dropbox \
    "/run/media/$USER/Backup"

date
