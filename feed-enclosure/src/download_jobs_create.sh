#!/bin/sh

# Adds a job to the download jobs recfile database.
#
# Runtime dependencies:
#   ./download_jobs_find_db.sh
#   apt install recutils # Version: 1.8-1
#
# Test dependencies:
#   ../tst/lint_shell.sh

set -e -u

DL_JOB_FIND_DB_BIN="${DL_JOB_FIND_DB_BIN:-$(dirname "$(readlink -e "$0")")/download_jobs_find_db.sh}"
RECINS_BIN="${RECINS_BIN:-recins}"

if [ $# -ne 3 ]; then
    echo "Usage: $(basename "$0") URL FORMAT FOLDER" >&2
    exit 1
fi

url="$1"
format="$2"
folder="$3"
shift 3

jobs_db="$("$DL_JOB_FIND_DB_BIN")"
mkdir -p "$(dirname "$jobs_db")"
touch "$jobs_db"

# TODO detect duplicates?
"$RECINS_BIN" \
    -f URL -v "$url" \
    -f Format -v "$format" \
    -f Folder -v "$folder" \
    "$jobs_db"
