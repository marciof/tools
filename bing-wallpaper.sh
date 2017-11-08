#!/bin/sh
# shellcheck disable=SC2039
set -e -u

app="$(basename "$0")"
api_url='http://www.bing.com/HPImageArchive.aspx?format=xml&idx=0&n=1&mkt=en-US'
img_path="$(curl -fs "$api_url" | sed -E 's|.+<url>([^<]+)</url>.+|\1|')"
img_url="http://www.bing.com$img_path"

logger --stderr --tag "$app" "image URL: $img_url"
has_found_selected=

for res_info in $(xrandr | grep -E '^ ' | tr -s ' ' : | cut -d: -f2,3); do
    res="$(printf %s "$res_info" | cut -d: -f1)"

    if [ -z "$has_found_selected" ]; then
        if printf %s "$res_info" | grep -qF '*'; then
            has_found_selected=Y
        else
            logger --stderr --tag "$app" "skip resolution: $res"
            continue
        fi
    fi
    
    new_img_url="$(printf %s "$img_url" | sed -E "s/[0-9]+x[0-9]+/$res/")"
    logger --stderr --tag "$app" "check resolution: $res"
    
    if curl -fsI "$new_img_url" >/dev/null; then
        img_url="$new_img_url"
        break
    fi
done

img_file=bing-wallpaper.jpg
logger --stderr --tag "$app" "download image URL: $img_url"
wget -qO "$img_file" "$img_url"

xfconf-query -c xfce4-desktop \
    -p /backdrop/screen0/monitor0/workspace0/last-image \
    -s "$(readlink -e "$img_file")"
