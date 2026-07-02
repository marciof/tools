#!/bin/sh

# KDE Plasma auto light/dark color scheme and wallpaper.
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
# - KDE Plasma docs: https://develop.kde.org/docs/plasma/theme/theme-details/#colors
# - KDE bug #433761: https://bugs.kde.org/show_bug.cgi?id=433761
# - KDE bug #446584: https://bugs.kde.org/show_bug.cgi?id=446584
# - KDE bug #433059: https://bugs.kde.org/show_bug.cgi?id=433059

set -e -u

script_file="$0"
base_path="$(dirname "$(realpath -e "$script_file")")"

help_opt=h
light_color_scheme_opt=l
light_wallpaper_opt=L
dark_color_scheme_opt=d
dark_wallpaper_opt=D

light_color_scheme=
light_wallpaper=
dark_color_scheme=
dark_wallpaper=

if [ $# -eq 0 ]; then
    set -- "-$help_opt"
fi

while getopts "$help_opt$light_color_scheme_opt:$light_wallpaper_opt:$dark_color_scheme_opt:$dark_wallpaper_opt:" opt "$@"; do
    case "$opt" in
        "$light_color_scheme_opt")
            light_color_scheme="$OPTARG"
            ;;
        "$light_wallpaper_opt")
            light_wallpaper="$OPTARG"
            ;;
        "$dark_color_scheme_opt")
            dark_color_scheme="$OPTARG"
            ;;
        "$dark_wallpaper_opt")
            dark_wallpaper="$OPTARG"
            ;;
        \?)
            printf "use '-%s' for help\n" "$help_opt" >&2
            exit 1
            ;;
        "$help_opt")
            printf 'usage: %s [options]\n\n' "$script_file"
            printf 'options:\n'
            printf '  -%s NAME\tname of light color scheme\n' "$light_color_scheme_opt"
            printf '  -%s NAME\tname of dark color scheme\n' "$dark_color_scheme_opt"
            printf '  -%s FILE\tpath to light wallpaper\n' "$light_wallpaper_opt"
            printf '  -%s FILE\tpath to dark wallpaper\n' "$dark_wallpaper_opt"
            exit 0
            ;;
    esac
done

shift "$((OPTIND - 1))"

"$base_path"/xdg-color-scheme.py -t "$@" | while read -r color; do
    case "$color" in
        light)
            if [ -n "$light_color_scheme" ]; then
                plasma-apply-colorscheme "$light_color_scheme"
            fi
            if [ -n "$light_wallpaper" ]; then
                plasma-apply-wallpaperimage "$light_wallpaper"
            fi
            ;;
        dark)
            if [ -n "$dark_color_scheme" ]; then
                plasma-apply-colorscheme "$dark_color_scheme"
            fi
            if [ -n "$dark_wallpaper" ]; then
                plasma-apply-wallpaperimage "$dark_wallpaper"
            fi
            ;;
    esac
done
