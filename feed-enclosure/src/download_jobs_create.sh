#!/bin/sh

# TODO document

set -e -u

# TODO check dependencies
FIND_DB_BIN="${FIND_DB_BIN:-$(dirname "$(readlink -e "$0")")/download_jobs_find_db.sh}"
RECINS_BIN="${RECINS_BIN:-recins}"

if [ $# -ne 3 ]; then
    echo "Usage: $(basename "$0") URL FORMAT FOLDER" >&2
    exit 1
fi

jobs_db="$("$FIND_DB_BIN")"

url="$1"
format="$2"
folder="$3"
shift 3

mkdir -p "$(dirname "$jobs_db")"
touch "$jobs_db"

# TODO detect duplicates?
# TODO add ID/hash for easier deletion?
"$RECINS_BIN" \
    -f URL -v "$url" \
    -f Format -v "$format" \
    -f Folder -v "$folder" \
    "$jobs_db"
