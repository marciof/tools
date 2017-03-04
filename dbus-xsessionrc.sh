#!/bin/bash

app="$(basename "$BASH_SOURCE" .sh)"
path=/org/freedesktop/login1
interface=org.freedesktop.login1.Manager

dbus-monitor --system --profile "type=signal,path=$path,interface=$interface" 2>/dev/null |
    while read type timestamp serial sender destination path interface member; do
        case "$member" in
            Session*)
                logger --stderr --tag "$app" "Got $member: Re-apply"
                source ~/.xsessionrc
        esac
    done
