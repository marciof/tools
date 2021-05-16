#!/bin/sh

# TODO document

set -e -u

# TODO check dependencies
FIND_DB_BIN="${FIND_DB_BIN:-$(dirname "$(readlink -e "$0")")/download_jobs_find_db.sh}"
JOB_DELETE_BIN="${JOB_DELETE_BIN:-$(dirname "$(readlink -e "$0")")/download_jobs_delete.sh}"
ENCLOSURE_DL_BIN="${ENCLOSURE_DL_BIN:-$(dirname "$(readlink -e "$0")")/enclosure_download.sh}"
RECSEL_BIN="${RECSEL_BIN:-recsel}"

job="$("$FIND_DB_BIN" | xargs "$RECSEL_BIN" -n 0)"
url="$(printf %s "$job" | "$RECSEL_BIN" -P URL)"
format="$(printf %s "$job" | "$RECSEL_BIN" -P Format)"
folder="$(printf %s "$job" | "$RECSEL_BIN" -P Folder)"

# TODO use generic download format option
# TODO loop over all pending download jobs
"$ENCLOSURE_DL_BIN" -y "$format" -f "$folder" -- "$url"

"$JOB_DELETE_BIN" "$url" "$format" "$folder"
