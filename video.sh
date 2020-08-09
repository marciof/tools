#!/bin/sh
set -e -u

show_usage() {
    echo "Usage: $(basename "$0") audio|smil <video> ..." >&2
    exit 1
}

if ! command -v ffmpeg >/dev/null; then
    echo 'FFmpeg not in $PATH: https://www.ffmpeg.org' >&2
    exit 1
fi

if [ $# -eq 0 ]; then
    show_usage
fi

action="$1"
shift

for video; do
    file="${video%.*}"

    if [ "$action" = audio ]; then
        if ffmpeg -i "$video" -v error -vn -acodec copy "$file.m4a"; then
            echo "OK: $video"
        else
            echo "ERROR: $video"
        fi
    elif [ "$action" = smil ]; then
        dimensions="$(ffprobe -v error -show_entries stream=height,width "$video")"
        height="$(echo "$dimensions" | grep height | grep -Eo '[0-9]+')"
        width="$(echo "$dimensions" | grep width | grep -Eo '[0-9]+')"

        date="$(stat -c %W,%X,%Y,%Z "$video" \
            | tr , '\n' \
            | grep -vE '^0$' \
            | sort -n \
            | head -n1 \
            | xargs printf '@%s' \
            | xargs date -I --date)"

        cat <<SMIL >"$file.smil"
<?xml version="1.1"?>
<smil xmlns="http://www.w3.org/ns/SMIL" version="3.0">
  <head>
    <meta name="Date" content="$date"/>
    <layout>
      <root-layout width="$width" height="$height"/>
      <region id="video" width="100%" height="100%"/>
    </layout>
  </head>
  <body>
    <video region="video" src="$(basename "$video")"/>
  </body>
</smil>
SMIL
    else
        show_usage
    fi
done
