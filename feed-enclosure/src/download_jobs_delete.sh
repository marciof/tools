#!/bin/sh

# Removes a job from a download jobs recfile database.
#
# Dependencies:
#   apt install recutils # Version: 1.8-1

set -e -u

RECDEL_BIN="${RECDEL_BIN:-recdel}"

if [ $# -ne 4 ]; then
    echo "Usage: $(basename "$0") URL FORMAT FOLDER DATABASE" >&2
    exit 1
fi

# Encode a string for use in a recutils selection expression.
#
# Arguments: string to encode
# Stdin: none
# Stdout: encoded and quoted string
encode_rec_string() {
    printf "'"
    # FIXME recdel is unable to find records with escaped quotes
    printf %s "$1" | sed -r "s/'/' \& \"'\" \& '/g"
    printf "'"
}

url="$(encode_rec_string "$1")"
format="$(encode_rec_string "$2")"
folder="$(encode_rec_string "$3")"
db="$4"
shift 4

"$RECDEL_BIN" \
    -e "URL = $url && Format = $format && Folder = $folder" \
    "$db"
