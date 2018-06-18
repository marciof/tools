#!/bin/sh
set -e -u
grep URL= < "$1" | cut -d= -f2 | xargs -n1 xdg-open
