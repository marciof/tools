#!/bin/sh

# TODO set DPI per screen/monitor

# Simple switcher for a multi-monitor setup with different DPIs.
#
# Arguments: DPI
# Stdin: none
# Stdout: none
#
# Runtime dependencies:
#   apt install xfconf # Version: 4.16.0-2
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u -x
dpi="$1"
xfconf-query --create -c xsettings -t int -p /Xft/DPI -s "$dpi"
