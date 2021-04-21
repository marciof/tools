#!/bin/sh

# Download handler for Liferea's feed enclosures.
#
# Arguments: URL path
# Stdin: none
# Stdout: download progress
#
# Runtime dependencies:
#   ./youtube_dl_wrapper.py
#   apt install uget # Version: 2.2.3-2 # download non-YouTube URLs
#   apt install ffmpeg # Version: 7:4.3.1-4ubuntu1 # merge video/audio
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

YOUTUBE_DL_BIN="${YOUTUBE_DL_BIN:-$(dirname "$(readlink -e "$0")")/youtube_dl_wrapper.py}"
UGET_BIN="${UGET_BIN:-uget-gtk}"

is_ign_daily_fix_url() {
    printf %s "$1" | grep -q -P '://assets\d*\.ign\.com/videos/'
}

upgrade_ign_daily_fix_url_res() {
    ign_width='[[:digit:]]+'
    ign_hash='[[:xdigit:]]+'
    ign_bitrate='[[:digit:]]+'

    printf %s "$1" \
        | sed -r "s#/$ign_width(/$ign_hash-)$ign_bitrate-#/1920\\13906000-#"
}

percent_decode() {
    sed -r 's/%([[:xdigit:]]{2})/\\x\1/g' | xargs -0 printf %b
}

extract_nice_filename_from_url() {
    if printf %s "$1" | grep -q -F '#'; then
        # FIXME: Liferea seems to percent-encode characters even when the URL
        #        fragment doesn't, so as a workaround decode them
        printf %s "$1" | sed -r 's/^[^#]+#//' | percent_decode
    fi
}

download_via_uget() {
    uget_url="$1"
    uget_path="$2"
    uget_filename="$(extract_nice_filename_from_url "$uget_url")"

    if [ -n "$uget_filename" ]; then
        set -- "--filename=$uget_filename"
    else
        set --
    fi

    # FIXME: uGet doesn't seem to interpret relative folder paths correctly,
    #        so as a workaround make it absolute
    "$UGET_BIN" \
        --quiet \
        "--folder=$(readlink -e -- "$uget_path")" \
        "$@" \
        -- \
        "$uget_url"
}

# TODO: getopt option for download path?
# TODO: GUI notification of download errors or significant events?
#       eg. ffmpeg muxing start/end, error "downloading" livestreams, etc
main() {
    if ! command -v "$YOUTUBE_DL_BIN" >/dev/null; then
        echo "Error: $YOUTUBE_DL_BIN not found (override \$YOUTUBE_DL_BIN)" >&2
        return 1
    fi

    if ! command -v "$UGET_BIN" >/dev/null; then
        echo "Error: $UGET_BIN not found (override \$UGET_BIN)" >&2
        return 1
    fi

    if [ $# -ne 2 ]; then
        cat <<'EOT' >&2
Arguments: url path
Note: if the URL has a URL fragment then it's an optional filename
EOT
        return 1
    fi

    url="$1"
    path="$2"
    shift 2

    if is_ign_daily_fix_url "$url"; then
        # TODO: missing metadata for IGN Daily Fix videos (maybe not needed?)
        # TODO: add IGN Daily Fix support to youtube-dl?
        #       https://github.com/ytdl-org/youtube-dl/tree/master#adding-support-for-a-new-site
        #       https://github.com/ytdl-org/youtube-dl/issues/24771
        download_via_uget "$(upgrade_ign_daily_fix_url_res "$url")" "$path"
    else
        (
            # FIXME: youtube-dl doesn't have an option for the output directory,
            #        so as a workaround go to where it should be downloaded
            cd -- "$path"

            # TODO: getopt option to control video quality?
            "$YOUTUBE_DL_BIN" \
                --verbose \
                --external-downloader uget \
                --add-metadata \
                --format bestvideo+bestaudio \
                -- \
                "$url"
        )
    fi
}

if [ -t 0 ]; then
    main "$@"
else
    # Format output with logging for when run by Liferea.
    {
        echo "Command line arguments: $0 $*"
        main "$@"
    } 2>&1 | logger --stderr --tag "$(basename "$0") [PID $$]"
fi
