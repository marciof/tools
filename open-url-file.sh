#!/bin/sh
# File handler for the ".url" file format.
#   [InternetShortcut]
#   URL=https://www.example.com

set -e -u
grep -m1 URL= <"$1" | sed -e 's/^URL\s*=\s*//' | xargs xdg-open
