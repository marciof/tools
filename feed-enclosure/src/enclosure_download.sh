#!/bin/sh

# TODO update dependencies list
# Wrapper script to download enclosures, that can be used with Liferea.
# Accepts whatever youtube-dl supports, plus IGN Daily Fix videos.
#
# Runtime dependencies:
#   ./youtube_dl_wrapper.py
#   apt install uget # Version: 2.2.3-2 # downloader tool
#   apt install ffmpeg # Version: 7:4.3.1-4ubuntu1 # merge video/audio
#
# Test dependencies:
#   ../tst/lint_shell.sh

set -e -u

YOUTUBE_DL_BIN="${YOUTUBE_DL_BIN:-$(dirname "$(readlink -e "$0")")/youtube_dl_wrapper.py}"
UGET_BIN="${UGET_BIN:-uget-gtk}"

help_opt=h
# TODO optional separate folder per show/feed/YouTube channel?
download_folder_opt=f
# TODO provide a generic download format option
ytdl_video_format_opt=y
dl_begin_script_opt=b
dl_end_script_opt=e

download_folder=.
ytdl_video_format=bestvideo+bestaudio
dl_begin_script=
dl_end_script=

check_dependencies() {
    if ! command -v "$YOUTUBE_DL_BIN" >/dev/null; then
        echo "Error: $YOUTUBE_DL_BIN not found (override \$YOUTUBE_DL_BIN)" >&2
        return 1
    fi

    if ! command -v "$UGET_BIN" >/dev/null; then
        echo "Error: $UGET_BIN not found (override \$UGET_BIN)" >&2
        return 1
    fi
}

# Check if a URL is for an IGN Daily Fix video.
#
# Arguments: URL
# Exit status: 0 when true
is_ign_daily_fix_url() {
    printf %s "$1" | grep -q -P '://assets\d*\.ign\.com/videos/'
}

# Modify a URL for an IGN Daily Fix video to have the highest resolution
# possible.
#
# Arguments: URL
# Stdin: none
# Stdout: modified URL
upgrade_ign_daily_fix_url_video_res() {
    ign_width='[[:digit:]]+'
    ign_hash='[[:xdigit:]]+'
    ign_bitrate='[[:digit:]]+'

    printf %s "$1" \
        | sed -r "s#/$ign_width(/$ign_hash-)$ign_bitrate-#/1920\\13906000-#"
}

# Decode a percent-encoded string.
# https://en.wikipedia.org/wiki/Percent-encoding
#
# Arguments: none
# Stdin: percent-encoded string
# Stdout: percent-decoded string
percent_decode() {
    sed -r 's/%([[:xdigit:]]{2})/\\x\1/g' | xargs -0 printf %b
}

# Extract an optional filename hint (for downloaders) from the URL fragment,
# if available.
#
# Arguments: URL
# Stdin: none
# Stdout: filename if available, otherwise no output
extract_nice_filename_from_url() {
    if printf %s "$1" | grep -q -F '#'; then
        # FIXME Liferea seems to percent-encode characters even when the URL
        #       fragment doesn't, so as a workaround decode them
        printf %s "$1" | sed -r 's/^[^#]+#//' | percent_decode
    fi
}

# Download a URL using uGet in the background.
#
# Globals: UGET_BIN
# Arguments: URL, folder path
# Stdin: none
# Stdout: log filename where uGet stdout and stderr are logged to
download_via_uget() {
    uget_url="$1"
    uget_folder="$2"
    uget_filename="$(extract_nice_filename_from_url "$uget_url")"

    if [ -n "$uget_filename" ]; then
        set -- "--filename=$uget_filename"
    else
        set --
    fi

    uget_log_file="$(mktemp)"
    echo "uGet log file: $uget_log_file"

    # FIXME uGet doesn't seem to interpret relative folder paths correctly,
    #       so as a workaround make it absolute
    nohup "$UGET_BIN" \
        --quiet \
        "--folder=$(readlink -e -- "$uget_folder")" \
        "$@" \
        -- \
        "$uget_url" </dev/null >"$uget_log_file" &
}

# TODO document
download_via_ytdl() {
    ytdl_url="$1"
    ytdl_format="$2"
    ytdl_folder="$3"

    (
        # FIXME youtube-dl doesn't have an option for the output directory
        cd -- "$ytdl_folder"

        # TODO resume downloads if process is never restarted
        # TODO what happens when offline?
        # TODO YouTube download URLs may expire, eg. queued in downloader
        "$YOUTUBE_DL_BIN" \
            --verbose \
            --external-downloader uget \
            --add-metadata \
            --format "$ytdl_format" \
            -- \
            "$ytdl_url"
    )
}

print_usage() {
    cat <<EOT >&2
Usage: $(basename "$0") [OPTION]... URL

Options:
  -$help_opt           display this help and exit
  -$download_folder_opt FOLDER    download save location to "FOLDER", defaults to "$download_folder"
  -$ytdl_video_format_opt FORMAT    set youtube-dl video "FORMAT", defaults to "$ytdl_video_format"
  -$dl_begin_script_opt SCRIPT    script to run when beginning a download
  -$dl_end_script_opt SCRIPT    script to run when ending a download

Notes:
  If the URL contains a fragment part, then it's an optional filename hint.
  Script hooks are passed the following arguments: URL FORMAT FOLDER
EOT
}

process_options() {
    while getopts "$download_folder_opt:$ytdl_video_format_opt:$help_opt$dl_begin_script_opt:$dl_end_script_opt:" process_opt "$@"; do
        case "$process_opt" in
            "$download_folder_opt")
                download_folder="$OPTARG"
                ;;
            "$ytdl_video_format_opt")
                ytdl_video_format="$OPTARG"
                ;;
            "$dl_begin_script_opt")
                dl_begin_script="$OPTARG"
                ;;
            "$dl_end_script_opt")
                dl_end_script="$OPTARG"
                ;;
            "$help_opt")
                print_usage
                return 1
                ;;
            ?)
                echo "Try '-$help_opt' for more information." >&2
                return 1
                ;;
        esac
    done
}

# TODO GUI notification of download errors or significant events?
#      eg. ffmpeg muxing start/end, error "downloading" livestreams, etc
main() {
    check_dependencies
    process_options "$@"
    shift $((OPTIND - 1))

    if [ $# -ne 1 ]; then
        print_usage
        return 1
    fi

    url="$1"
    shift

    if [ -n "$dl_begin_script" ]; then
      "$dl_begin_script" "$url" "$ytdl_video_format" "$download_folder"
    fi

    if is_ign_daily_fix_url "$url"; then
        # TODO missing metadata for IGN Daily Fix videos (maybe not needed?)
        # TODO missing youtube-dl's workaround for uGet Unicode filenames
        # TODO add IGN Daily Fix support to youtube-dl?
        #      https://github.com/ytdl-org/youtube-dl/tree/master#adding-support-for-a-new-site
        #      https://github.com/ytdl-org/youtube-dl/issues/24771
        download_via_uget \
            "$(upgrade_ign_daily_fix_url_video_res "$url")" \
            "$download_folder"
    else
        download_via_ytdl "$url" "$ytdl_video_format" "$download_folder"
    fi

    # TODO wait for `download_via_uget` to finish the download
    if [ -n "$dl_end_script" ]; then
      "$dl_end_script" "$url" "$ytdl_video_format" "$download_folder"
    fi
}

if [ -t 0 ]; then
    main "$@"
else
    # Format output with logging for when run outside the terminal.
    {
        echo "Command line arguments: $0 $*"
        main "$@"
    } 2>&1 | logger --stderr --tag "$(basename "$0") [PID $$]"
fi
