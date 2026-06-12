#!/bin/sh

# File handler for the `.url` file format (MS Windows 95 Internet shortcut),
# passing the URL to `xdg-open`.
#
# Arguments: <file>
#
# Dependencies (runtime): xdg-utils
# Dependencies (test): shellcheck

set -o errexit -o nounset

SCRIPT_FILENAME="$(basename "$(realpath -e "$0")")"

# Arguments: [output file] ...
log_and_cat() {
    while IFS= read -r line; do
        logger --tag "$SCRIPT_FILENAME" -- "$line"
        echo "$line"

        for output; do
            echo "$line" >"$output"
        done
    done
}

for url_file; do
    log_and_cat <"$url_file" \
        | grep --extended-regexp --max-count 1 '\s*URL\s*=' \
        | cut --delimiter = --fields 2- \
        | log_and_cat /dev/tty \
        | xargs xdg-open
done
