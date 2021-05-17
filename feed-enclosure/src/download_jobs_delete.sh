#!/bin/sh

# Removes a job from the download jobs recfile database.
#
# Runtime dependencies:
#   ./download_jobs_find_db.sh
#   apt install recutils # Version: 1.8-1
#
# Test dependencies:
#   ../tst/lint_shell.sh

set -e -u

DL_JOB_FIND_DB_BIN="${DL_JOB_FIND_DB_BIN:-$(dirname "$(readlink -e "$0")")/download_jobs_find_db.sh}"
RECDEL_BIN="${RECDEL_BIN:-recdel}"

if ! command -v "$DL_JOB_FIND_DB_BIN" >/dev/null; then
    echo "Error: $DL_JOB_FIND_DB_BIN not found (override \$DL_JOB_FIND_DB_BIN)" >&2
    exit 1
fi

if ! command -v "$RECDEL_BIN" >/dev/null; then
    echo "Error: $RECDEL_BIN not found (override \$RECDEL_BIN)" >&2
    exit 1
fi

if [ $# -ne 3 ]; then
    echo "Usage: $(basename "$0") URL FORMAT FOLDER" >&2
    exit 1
fi

# FIXME recdel is unable to find records with escaped quotes
encode_rec_string() {
    printf "'"
    printf %s "$1" | sed -r "s/'/' \& \"'\" \& '/g"
    printf "'"
}

url="$(encode_rec_string "$1")"
format="$(encode_rec_string "$2")"
folder="$(encode_rec_string "$3")"
shift 3

"$DL_JOB_FIND_DB_BIN" | xargs "$RECDEL_BIN" \
    -e "URL = $url && Format = $format && Folder = $folder"
