#!/bin/sh

# File handler for the `.url` file format (MS Windows 95 Internet shortcut),
# passing the URL to `xdg-open`.
#
# Arguments: <file>
#
# Dependencies (runtime): xdg-utils
# Dependencies (test): shellcheck

set -o errexit -o nounset -o xtrace

grep --extended-regexp --max-count 1 '\s*URL\s*=' -- "$1" \
    | cut --delimiter = --fields 2- \
    | xargs xdg-open
