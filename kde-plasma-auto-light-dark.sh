#!/bin/sh

# KDE Plasma auto light/dark settings.
#
# How to change active/inactive titlebar color:
#
# 1. Copy an existing color scheme (`Edit Color Scheme` and `Save As`)
#    that has active/inactive titlebar colors.
# 2. Ensure there aren't any `[Colors:Header]` and `[Colors:Header][Inactive]`
#    sections in the new color scheme file.
# 3. Ensure there is a `[WM]` section in the new color scheme file, which
#    will have the active/inactive titlebar colors.
#
# References:
#
# - XDG Settings: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html
# - KDE Plasma docs: https://develop.kde.org/docs/plasma/theme/theme-details/#colors
# - KDE bug #433761: https://bugs.kde.org/show_bug.cgi?id=433761
# - KDE bug #446584: https://bugs.kde.org/show_bug.cgi?id=446584
# - KDE bug #433059: https://bugs.kde.org/show_bug.cgi?id=433059
#
# See also:
#
# - Yin-Yang: https://github.com/oskarsh/Yin-Yang
# - Koi: https://github.com/baduhai/Koi
# - auto-knight: https://github.com/DimseBoms/auto-knight
# - Blueblack: https://github.com/smitropoulos/blueblack
# - darkman: https://gitlab.com/WhyNotHugo/darkman
# - KDE Night Light Dimming: https://github.com/DefendTheDisabled/KDE-night-light-dimming
#
# Dependencies (runtime): dbus-bin plasma-workspace libkf6config-bin
# Dependencies (test): shellcheck

set -o errexit -o nounset

SCRIPT_FILENAME="$(basename "$(realpath -e "$0")")"

log_cat() {
    while IFS= read -r line; do
        logger --id $$ --tag "$SCRIPT_FILENAME" -- \
            "$(printf "%s: %s\n" "$1" "$line")"
        echo "$line"
    done
}

current_color_scheme_id() {
    dbus-send \
        --print-reply=literal \
        --dest=org.freedesktop.portal.Desktop \
        /org/freedesktop/portal/desktop \
        org.freedesktop.portal.Settings.ReadOne \
        string:org.freedesktop.appearance \
        string:color-scheme \
    | log_cat 'D-Bus color-scheme' \
    | awk '{print $NF}' \
    | log_cat 'Color scheme ID'
}

current_color_scheme() {
    case "$(current_color_scheme_id)" in
        1) echo dark;;
        2) echo light;;
        *) echo none;;
    esac \
    | log_cat 'Color scheme name'
}

monitor_color_scheme() {
    dbus-monitor "interface='org.freedesktop.portal.Settings',member='SettingChanged'" \
    | while IFS= read -r line; do
        case "$line" in
            *color-scheme*)
                current_color_scheme;;
        esac
    done
}

throttle() {
    last_time_secs=0

    while IFS= read -r line; do
        current_time_secs="$(date +%s)"

        if [ "$current_time_secs" -ge "$((last_time_secs + 1))" ]; then
            last_time_secs="$current_time_secs"
            echo "$line"
        fi
    done
}

run() {
    "$@"
}

dry_run() {
    printf '[dry-run] %s\n' "$*"
}

help_opt=h
dry_run_opt=n

light_color_scheme_opt=l
light_wallpaper_opt=L
dark_color_scheme_opt=d
dark_wallpaper_opt=D

light_color_scheme=
light_wallpaper=
dark_color_scheme=
dark_wallpaper=

run_cmd=run
has_required_args=false

echo "$*" | log_cat 'Arguments' >/dev/null

while getopts "$help_opt$dry_run_opt$light_color_scheme_opt:$light_wallpaper_opt:$dark_color_scheme_opt:$dark_wallpaper_opt:" opt "$@"; do
    case "$opt" in
        "$light_color_scheme_opt")
            light_color_scheme="$OPTARG"
            has_required_args=true
            ;;
        "$light_wallpaper_opt")
            light_wallpaper="$(realpath -e "$OPTARG")"
            has_required_args=true
            ;;
        "$dark_color_scheme_opt")
            dark_color_scheme="$OPTARG"
            has_required_args=true
            ;;
        "$dark_wallpaper_opt")
            dark_wallpaper="$(realpath -e "$OPTARG")"
            has_required_args=true
            ;;
        "$dry_run_opt")
            run_cmd=dry_run
            ;;
        \?)
            printf "try '-%s' for help\n" "$help_opt" >&2
            exit 1
            ;;
        "$help_opt")
            printf 'usage: %s [options]\n\n' "$SCRIPT_FILENAME"
            printf 'options:\n'
            printf '  -%s NAME\tname of light color scheme\n' "$light_color_scheme_opt"
            printf '  -%s NAME\tname of dark color scheme\n' "$dark_color_scheme_opt"
            printf '  -%s FILE\tpath to light wallpaper\n' "$light_wallpaper_opt"
            printf '  -%s FILE\tpath to dark wallpaper\n' "$dark_wallpaper_opt"
            printf '  -%s \t\tdry-run\n' "$dry_run_opt"
            printf '  -%s \t\thelp\n' "$help_opt"
            exit 0
            ;;
    esac
done

shift "$((OPTIND - 1))"

if [ $# -gt 0 ] || ! "$has_required_args"; then
    echo 'Invalid or missing required arguments' >&2
    printf "try '-%s' for help\n" "$help_opt" >&2
    exit 1
fi

{
    current_color_scheme
    monitor_color_scheme
} \
| throttle \
| log_cat 'Throttled color scheme change' \
| while IFS= read -r color; do
    case "$color" in
        light)
            if [ -n "$light_color_scheme" ]; then
                "$run_cmd" plasma-apply-colorscheme "$light_color_scheme"
            fi
            if [ -n "$light_wallpaper" ]; then
                "$run_cmd" plasma-apply-wallpaperimage "$light_wallpaper"

                # FIXME lockscreen only updated if not in use
                "$run_cmd" kwriteconfig6 \
                    --file kscreenlockerrc \
                    --group Greeter \
                    --group Wallpaper \
                    --group org.kde.image \
                    --group General \
                    --key Image "file://$light_wallpaper"
            fi
            ;;
        dark)
            if [ -n "$dark_color_scheme" ]; then
                "$run_cmd" plasma-apply-colorscheme "$dark_color_scheme"
            fi
            if [ -n "$dark_wallpaper" ]; then
                "$run_cmd" plasma-apply-wallpaperimage "$dark_wallpaper"

                # FIXME lockscreen only updated if not in use
                "$run_cmd" kwriteconfig6 \
                    --file kscreenlockerrc \
                    --group Greeter \
                    --group Wallpaper \
                    --group org.kde.image \
                    --group General \
                    --key Image "file://$dark_wallpaper"
            fi
            ;;
        *)
            echo "Unsupported color scheme: $color" >&2
            ;;
    esac
done \
| log_cat 'Status'
