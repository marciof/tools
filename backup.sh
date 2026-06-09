#!/bin/sh

set -o errexit -o nounset -o xtrace

date
rsync \
    --archive --partial --delete --executability --atimes --no-links \
    --human-readable --info=progress2 \
    --exclude=.dropbox.cache \
    ~/Dropbox \
    "/run/media/$USER/Backup"
date
