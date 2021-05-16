#!/bin/sh

# TODO document

set -e -u

# TODO check dependencies
DL_JOB_FIND_DB_BIN="${DL_JOB_FIND_DB_BIN:-$(dirname "$(readlink -e "$0")")/download_jobs_find_db.sh}"
RECDEL_BIN="${RECDEL_BIN:-recdel}"

if [ $# -ne 3 ]; then
    echo "Usage: $(basename "$0") URL FORMAT FOLDER" >&2
    exit 1
fi

# TODO document
encode_rec_string() {
    printf "'"
    printf %s "$1" | sed -r "s/'/' \& \"'\" \& '/g"
    printf "'"
}

url="$(encode_rec_string "$1")"
format="$(encode_rec_string "$2")"
folder="$(encode_rec_string "$3")"
shift 3

# TODO use optional ID/hash for easier deletion?
"$DL_JOB_FIND_DB_BIN" | xargs "$RECDEL_BIN" \
    -e "URL = $url && Format = $format && Folder = $folder"
