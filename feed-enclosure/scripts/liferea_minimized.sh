#!/bin/sh

# Starts Liferea in the background and minimizes it.
# https://github.com/lwindolf/liferea/issues/447
#
# Arguments: passthrough to Liferea
#
# Dependencies:
#   apt install liferea # Version: 1.13.1-1
#   apt install xdotool # Version: 1:3.20160805.1-4

set -e -u

LIFEREA_BIN="${LIFEREA_BIN:-liferea}"
XDOTOOL_BIN="${XDOTOOL_BIN:-xdotool}"

# Search for a visible window by class name.
#
# Globals: XDOTOOL_BIN
# Arguments: passthrough
# Stdout: search results
xdotool_search() {
    "$XDOTOOL_BIN" search --onlyvisible --classname "$@"
}

classname=Liferea

# TODO possible race-condition
# TODO sometimes not minimized on startup
if ! xdotool_search "$classname" windowminimize >/dev/null; then
    log_file="$(mktemp)"
    echo "Liferea log file: $log_file"

    nohup "$LIFEREA_BIN" "$@" </dev/null >"$log_file" &
    xdotool_search --sync "$classname" windowminimize
fi
