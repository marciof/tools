#!/bin/sh

# Download handler for Liferea's feed enclosures.
#
# Input: none
# Output: download progress
#
# Runtime dependencies:
#   python3 -m pip install youtube_dl # download Youtube videos
#   apt install uget # Version: 2.2.3-2 # download non-YouTube URLs
#   apt install ffmpeg # Version: 7:4.3.1-4ubuntu1 # merge video/audio
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

YOUTUBE_DL_BIN="${YOUTUBE_DL_BIN:-youtube-dl}"
UGET_BIN="${UGET_BIN:-uget-gtk}"

is_ign_daily_fix_url() {
    echo "$1" | grep -q -P '://assets\d*\.ign\.com/videos/'
}

prepare_ign_daily_fix_url() {
    ign_width='[[:digit:]]+'
    ign_hash='[[:xdigit:]]+'
    ign_bitrate='[[:digit:]]+'

    echo "$1" \
        | sed -r "s#/$ign_width(/$ign_hash-)$ign_bitrate-#/1920\\13906000-#"
}

main() {
    if ! command -v "$YOUTUBE_DL_BIN" >/dev/null; then
        echo "Error: $YOUTUBE_DL_BIN not found (override \$YOUTUBE_DL_BIN)" >&2
        return 1
    fi

    if [ $# -ne 2 ]; then
        echo 'Arguments: url path' >&2
        return 1
    fi

    url="$1"
    path="$2"
    shift 2

    if is_ign_daily_fix_url "$url"; then
        prepare_ign_daily_fix_url "$url" \
            | xargs "$UGET_BIN" --quiet "--folder=$(readlink -e "$path")"
    else
        (
            # Navigate to where the file should be downloaded to since
            # youtube-dl doesn't have an option for the output directory.
            cd "$path"
            "$YOUTUBE_DL_BIN" --add-metadata -f 'bestvideo+bestaudio' "$url"
        )
    fi
}

if [ -t 0 ]; then
    main "$@"
else
    # Tailor output with logging for when run under Liferea.
    app="$(basename "$0")"
    {
        echo "$@"
        main "$@"
    } 2>&1 | logger --stderr --tag "$app"
fi
