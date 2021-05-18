#!/bin/sh

# Prints the path to Liferea's OPML file (may not exist).
# https://lzone.de/liferea/faq.htm#how-to-copy-remote

set -e -u
echo "${XDG_CONFIG_HOME:-$HOME/.config}/liferea/feedlist.opml"
