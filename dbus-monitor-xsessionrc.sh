#!/bin/sh

# Monitors session changes through D-Bus and re-applies `~/.xsessionrc`.
#
# Arguments: none
# Stdin: none
# Stdout: none
#
# Runtime dependencies:
#   apt install dbus # Version: 1.12.20-1ubuntu1 # monitor D-Bus
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

app="$(basename "$0")"
path='path=/org/freedesktop/login1'
interface='interface=org.freedesktop.login1.Manager'

# TODO: not working on Xubuntu 20.10 x86-64?
# shellcheck disable=SC2034
dbus-monitor --system --profile "type=signal,$path,$interface" 2>/dev/null |
    while read -r type timestamp serial sender dest path interface member; do
        case "$member" in
            Session*)
                logger --stderr --tag "$app" "got $member: re-apply"
                (sh ~/.xsessionrc 2>&1 || true) | logger --stderr --tag "$app"
        esac
    done
