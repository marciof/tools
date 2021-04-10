#!/bin/sh

# Download handler for Liferea's feed enclosures.
#
# Input: none
# Output: download progress
#
# Runtime dependencies:
#   python3 -m pip install youtube_dl # for downloading Youtube videos
#   apt install ffmpeg # Version: 7:4.3.1-4ubuntu1 # for merging video/audio
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

main() {
    YOUTUBE_DL_BIN="${YOUTUBE_DL_BIN:-youtube-dl}"

    if ! command -v "$YOUTUBE_DL_BIN" >/dev/null; then
        echo "Error: $YOUTUBE_DL_BIN not found (override \$YOUTUBE_DL_BIN)" >&2
        exit 1
    fi

    if [ $# -ne 2 ]; then
        cat <<'EOT' >&2
Arguments: url path
EOT
        exit 1
    fi

    url="$1"
    path="$2"
    shift 2

    cd "$path"
    "$YOUTUBE_DL_BIN" --add-metadata --format 'bestvideo+bestaudio' "$url"
}

if [ -t 0 ]; then
    main "$@"
else
    # Tailor output with logging for when run under Liferea.
    app="$(basename "$0")"
    main "$@" 2>&1 | logger --stderr --tag "$app"
fi
