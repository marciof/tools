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

if ! command -v "$DL_JOB_FIND_DB_BIN" >/dev/null; then
    echo "Error: $DL_JOB_FIND_DB_BIN not found (override \$DL_JOB_FIND_DB_BIN)" >&2
    exit 1
fi

if ! command -v "$RECINS_BIN" >/dev/null; then
    echo "Error: $RECINS_BIN not found (override \$RECINS_BIN)" >&2
    exit 1
fi

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
