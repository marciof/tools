#!/bin/sh

# Creates a SMIL file per video file, with its dimensions and date.
#
# Arguments: file ...
# Stdin: none
# Stdout: tab separated lines, one per video: video filename, SMIL filename
#
# Runtime dependencies:
#   apt install ffmpeg # Version: 7:4.3.1-4ubuntu1 # get video dimensions
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

for video_file; do
    basename="${video_file%.*}"
    smil_file="$basename.smil"

    dimensions="$(ffprobe -v error -show_entries stream=height,width "$video_file")"
    height="$(echo "$dimensions" | grep height | cut -d= -f2)"
    width="$(echo "$dimensions" | grep width | cut -d= -f2)"

    date="$(stat -c %W,%X,%Y,%Z "$video_file" \
        | tr , '\n' \
        | grep -vE '^0$' \
        | sort -n \
        | head -n1 \
        | xargs printf '@%s' \
        | xargs date -I --date)"

    cat <<SMIL >"$smil_file"
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
    <video region="video" src="$(basename "$video_file")"/>
  </body>
</smil>
SMIL

    printf '%s\t%s\n' "$video_file" "$smil_file"
done
