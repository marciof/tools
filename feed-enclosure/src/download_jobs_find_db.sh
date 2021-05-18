#!/bin/sh

# Prints the path to the download jobs recfile database (may not exist).
# https://www.gnu.org/software/recutils/

set -e -u
echo "${XDG_CONFIG_HOME:-$HOME/.config}/feed-enclosure/download-jobs.rec"
