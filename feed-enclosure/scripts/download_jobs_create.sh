#!/bin/sh

# Adds a job to a download jobs recfile database.
# No attempt is made to detect duplicates.
#
# Dependencies:
#   apt install recutils # Version: 1.8-1

set -e -u
RECINS_BIN="${RECINS_BIN:-recins}"

if [ $# -ne 4 ]; then
    echo 'Usage: url format folder database' >&2
    exit 1
fi

url="$1"
format="$2"
folder="$3"
database="$4"
shift 4

mkdir -p "$(dirname "$database")"
touch "$database"

"$RECINS_BIN" \
    -f URL -v "$url" \
    -f Format -v "$format" \
    -f Folder -v "$folder" \
    "$database"
