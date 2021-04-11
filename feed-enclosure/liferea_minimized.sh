#!/bin/sh

# Starts Liferea in the background and minimizes it.
# https://github.com/lwindolf/liferea/issues/447
#
# Arguments: passthrough to Liferea
# Stdin: none
# Stdout: none
#
# Runtime dependencies:
#   apt install liferea # Version: 1.13.1-1
#   apt install xdotool # Version: 1:3.20160805.1-4
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

LIFEREA_BIN="${LIFEREA_BIN:-liferea}"

if ! command -v "$LIFEREA_BIN" >/dev/null; then
    echo "Error: $LIFEREA_BIN not found (override \$LIFEREA_BIN)" >&2
    exit 1
fi

liferea "$@" &
exit_status=$?
xdotool search --onlyvisible --classname --sync Liferea windowminimize
exit $exit_status
