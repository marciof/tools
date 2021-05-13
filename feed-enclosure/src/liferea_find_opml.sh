#!/bin/sh

# Prints the path to Liferea's OPML file (may not exist).
# https://lzone.de/liferea/faq.htm#how-to-copy-remote
#
# Arguments: none
# Stdin: none
# Stdout: path to Liferea's OPML file
#
# Test dependencies:
#   ../tst/lint_shell.sh

set -e -u

USER_CONFIG_PATH="${XDG_CONFIG_HOME:-$HOME/.config}"
LIFEREA_CONFIG_PATH="$USER_CONFIG_PATH/liferea"

printf '%s\n' "$LIFEREA_CONFIG_PATH/feedlist.opml"
