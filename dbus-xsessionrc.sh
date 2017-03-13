#!/bin/sh
set -e -u

app="$(basename "$0" .sh)"
path='path=/org/freedesktop/login1'
interface='interface=org.freedesktop.login1.Manager'

dbus-monitor --system --profile "type=signal,$path,$interface" 2>/dev/null |
    while read type timestamp serial sender dest path interface member; do
        case "$member" in
            Session*)
                logger --stderr --tag "$app" "got $member: re-apply"
                sh ~/.xsessionrc || true
        esac
    done
