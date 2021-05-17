#!/bin/sh

# Prints the path to the download jobs recfile database (may not exist).
# https://www.gnu.org/software/recutils/

set -e -u

USER_CONFIG_PATH="${XDG_CONFIG_HOME:-$HOME/.config}"
echo "$USER_CONFIG_PATH/feed-enclosure/download-jobs.rec"
