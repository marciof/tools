#!/bin/sh
set -e -u
grep URL= < "$1" | sed -e 's/^URL\s*=\s*//' | xargs -n1 xdg-open
