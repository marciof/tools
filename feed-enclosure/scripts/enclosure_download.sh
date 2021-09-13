#!/bin/sh

# Wrapper script to download enclosures, that can be used with Liferea.
# Accepts whatever youtube-dl supports, plus IGN Daily Fix videos.
#
# Dependencies:
#   ./youtube_dl_wrapper.py
#   apt install uget # Version: 2.2.3-2 # downloader tool
#   apt install ffmpeg # Version: 7:4.3.1-4ubuntu1 # merge video/audio

# TODO update dependencies

set -e -u

PYTHONPATH="${PYTHONPATH:-}:$(dirname "$(readlink -e "$0")")/../"
PYTHON3="${PYTHON3:-python3}"
UGET_BIN="${UGET_BIN:-uget-gtk}"

help_opt=h
# TODO option for folder per YouTube channel?
download_folder_opt=f
# TODO provide a generic download format option?
ytdl_video_format_opt=y
dl_hook_arg_opt=a
dl_begin_hook_opt=b
dl_end_hook_opt=e

download_folder=.
ytdl_video_format=bestvideo+bestaudio
dl_hook_arg=
dl_begin_hook=
dl_end_hook=

# Check if a URL is for IGN.
#
# Arguments: url
# Exit status: 0 when true
is_ign_url() {
    printf %s "$1" | grep -q -P '\.ign\.com/'
}

# Decode a percent-encoded string.
# https://en.wikipedia.org/wiki/Percent-encoding
#
# Stdin: percent-encoded string
# Stdout: percent-decoded string
percent_decode() {
    sed -r 's/%([[:xdigit:]]{2})/\\x\1/g' | xargs -0 printf %b
}

# Extract an optional filename hint (for downloaders) from the URL fragment,
# if available.
#
# Arguments: url
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
# Arguments: url folder
# Stdout: log filename where uGet stdout and stderr are logged to
download_via_uget() {
    dl_uget_url="$1"
    dl_uget_folder="$2"
    dl_uget_filename="$(extract_nice_filename_from_url "$dl_uget_url")"

    if [ -n "$dl_uget_filename" ]; then
        set -- "--filename=$dl_uget_filename"
    else
        set --
    fi

    "$PYTHON3" -m feed_enclosure.uget \
        --x-wait-download \
        --quiet \
        "--folder=$dl_uget_folder" \
        "$@" \
        "$dl_uget_url"
}

# Download a URL using youtube-dl.
#
# Globals: YOUTUBE_DL_BIN
# Arguments: url format folder
# Stdout: download progress
download_via_ytdl() {
    dl_ytdl_url="$1"
    dl_ytdl_format="$2"
    dl_ytdl_folder="$3"

    # TODO what happens when offline?
    # TODO YouTube download URLs may expire, eg. queued in downloader
    # TODO detect and skip livestreams?
    # TODO use xattrs? 
    # TODO embed thumbnail? 
    # TODO embed subtitles?
    # TODO remove sponsor blocks in videos?
    "$PYTHON3" -m feed_enclosure.youtube_dl \
        --external-downloader uget \
        --output "$dl_ytdl_folder" \
        --format "$dl_ytdl_format" \
        --add-metadata \
        --verbose \
        -- \
        "$dl_ytdl_url"
}

print_usage() {
    cat <<EOT >&2
Usage: [options] url

Options:
  -$help_opt           display this help and exit
  -$download_folder_opt folder    download save location to "folder", defaults to "$download_folder"
  -$ytdl_video_format_opt format    set youtube-dl video "format", defaults to "$ytdl_video_format"
  -$dl_begin_hook_opt command   "command" hook to run when beginning a download
  -$dl_end_hook_opt command   "command" hook to run when ending a download
  -$dl_hook_arg_opt argument  additional "argument" for the download hooks

Notes:
  If the URL contains a fragment part, then it's an optional filename hint.
  Download hooks are passed the following: url format folder argument
EOT
}

process_options() {
    while getopts "$download_folder_opt:$ytdl_video_format_opt:$help_opt$dl_begin_hook_opt:$dl_end_hook_opt:$dl_hook_arg_opt:" process_opt "$@"; do
        case "$process_opt" in
            "$download_folder_opt")
                download_folder="$OPTARG"
                ;;
            "$ytdl_video_format_opt")
                ytdl_video_format="$OPTARG"
                ;;
            "$dl_begin_hook_opt")
                dl_begin_hook="$OPTARG"
                ;;
            "$dl_end_hook_opt")
                dl_end_hook="$OPTARG"
                ;;
            "$dl_hook_arg_opt")
                dl_hook_arg="$OPTARG"
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
# TODO option to download from a list of URLs?
main() {
    process_options "$@"
    shift $((OPTIND - 1))

    if [ $# -ne 1 ]; then
        print_usage
        return 1
    fi

    export PYTHONPATH
    url="$1"
    shift

    if [ -n "$dl_begin_hook" ]; then
        "$dl_begin_hook" \
            "$url" "$ytdl_video_format" "$download_folder" "$dl_hook_arg"
    fi

    # TODO invert condition to let youtube-dl try first?
    # TODO attempt to extract metadata from IGN Daily Fix videos?
    if is_ign_url "$url"; then
        download_via_uget "$url" "$download_folder"
    else
        download_via_ytdl "$url" "$ytdl_video_format" "$download_folder"
    fi

    if [ -n "$dl_end_hook" ]; then
        "$dl_end_hook" \
            "$url" "$ytdl_video_format" "$download_folder" "$dl_hook_arg"
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
