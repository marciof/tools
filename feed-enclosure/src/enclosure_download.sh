#!/bin/sh

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
RECINS_BIN="${RECINS_BIN:-recins}"
RECDEL_BIN="${RECDEL_BIN:-recdel}"
RECSEL_BIN="${RECSEL_BIN:-recsel}"
# TODO update dependencies list on recutils

USER_CONFIG_PATH="${XDG_CONFIG_HOME:-$HOME/.config}"
FEED_ENCLOSURE_CONFIG_PATH="$USER_CONFIG_PATH/feed-enclosure"
JOB_DB_PATH="$FEED_ENCLOSURE_CONFIG_PATH/download-jobs.rec"

help_opt=h
# TODO optional separate folder per show/feed/YouTube channel?
download_folder_opt=f
# TODO make the video format option generic and not tied to youtube-dl?
ytdl_video_format_opt=y

download_folder=.
ytdl_video_format=bestvideo+bestaudio

# TODO document
# TODO detect duplicates?
# TODO use hooks to avoid polluting this script? easier to download one-offs?
record_job() {
    job_db="$1"
    job_url="$2"
    job_format="$3"
    job_folder="$4"

    mkdir -p "$(dirname "$job_db")"
    touch "$job_db"

    "$RECINS_BIN" \
        -f URL -v "$job_url" \
        -f Format -v "$job_format" \
        -f Folder -v "$job_folder" \
        "$job_db"
}

# TODO document
encode_rec_string() {
    printf "'"
    printf %s "$1" | sed -r "s/'/' \& \"'\" \& '/g"
    printf "'"
}

# TODO document
complete_job() {
    job_db="$1"
    job_url="$(encode_rec_string "$2")"
    job_format="$(encode_rec_string "$3")"
    job_folder="$(encode_rec_string "$4")"

    "$RECDEL_BIN" \
        -e "URL = $job_url && Format = $job_format && Folder = $job_folder" \
        "$job_db"
}

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
Usage: $(basename "$0") [OPTION]... [URL]

Note:
  If the URL contains a fragment part, then it's an optional filename hint.
  If no URL is given, then it resumes downloads that didn't finish.

Options:
  -$help_opt           display this help and exit
  -$download_folder_opt PATH      download save location to "PATH", defaults to "$download_folder"
  -$ytdl_video_format_opt FORMAT    set youtube-dl video "FORMAT", defaults to "$ytdl_video_format"
EOT
}

process_options() {
    while getopts "$download_folder_opt:$ytdl_video_format_opt:$help_opt" process_opt "$@"; do
        case "$process_opt" in
            "$download_folder_opt")
                download_folder="$OPTARG"
                ;;
            "$ytdl_video_format_opt")
                ytdl_video_format="$OPTARG"
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

    if [ $# -eq 0 ]; then
        "$RECSEL_BIN" "$JOB_DB_PATH"
        return 0
    elif [ $# -eq 1 ]; then
        url="$1"
        shift
    else
        print_usage
        return 1
    fi

    record_job "$JOB_DB_PATH" "$url" "$ytdl_video_format" "$download_folder"

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

    complete_job "$JOB_DB_PATH" "$url" "$ytdl_video_format" "$download_folder"
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
