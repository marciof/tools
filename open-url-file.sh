#!/bin/sh

# File handler for the ".url" file format (MS Windows 95 Internet shortcut),
# passing the URL to `xdg-open`.
#
# Example:
#   [InternetShortcut]
#   URL=https://www.example.com
#
# Arguments: file
# Stdin: none
# Stdout: none
#
# Runtime dependencies:
#   apt install xdg-utils # Version: 1.1.3-2ubuntu1.20.10.2 # open URL
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u
grep -m1 URL= <"$1" | sed -e 's/^URL\s*=\s*//' | xargs xdg-open
