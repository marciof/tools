#!/bin/sh
# Git (prepare-)commit message hook for adding issue numbers.

message_file=$1

for ref in '@{u}' HEAD; do
    issue="$(git rev-parse --abbrev-ref "$ref" 2> /dev/null \
        | grep -oE '[[:alpha:]]+-[[:digit:]]+$')"

    if [ -n "$issue" ]; then
        if [ "$(basename "$0")" = prepare-commit-msg ]; then
            printf "# Issue: %s\n#\n" "$issue" >> "$message_file"
        elif grep -vE "^[[:space:]]*(#|$)" "$message_file" \
                | head -n1 \
                | grep -qvF "[$issue]"; then
            sed -i.bak -e "1s/^/\[$issue\] /" "$message_file"
        fi

        break
    fi
done