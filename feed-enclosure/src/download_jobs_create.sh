#!/bin/sh

# Adds a job to a download jobs recfile database.
#
# Dependencies:
#   apt install recutils # Version: 1.8-1

set -e -u

RECINS_BIN="${RECINS_BIN:-recins}"

if [ $# -ne 4 ]; then
    echo "Usage: $(basename "$0") URL FORMAT FOLDER DATABASE" >&2
    exit 1
fi

url="$1"
format="$2"
folder="$3"
db="$4"
shift 4

mkdir -p "$(dirname "$db")"
touch "$db"

# TODO detect duplicates?
"$RECINS_BIN" \
    -f URL -v "$url" \
    -f Format -v "$format" \
    -f Folder -v "$folder" \
    "$db"
