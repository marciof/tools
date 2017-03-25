#!/bin/sh
set -e -u

buffer_file="$(mktemp)"
trap 'rm "$buffer_file"' EXIT

# FIXME: Using `head` stops `git` paging output abruptly.
head -n "$(($(tput lines) / 2))" > "$buffer_file"

if ! IFS= read -r line; then
    cat "$buffer_file"
    exit $?
fi

pager_fifo="$(mktemp -u)"
mkfifo "$pager_fifo"

pipe_to_pager_fifo() {
    trap 'rm "$buffer_file" "$pager_fifo"' EXIT
    cat "$buffer_file" > "$pager_fifo"
    echo "$line" > "$pager_fifo"
    cat > "$pager_fifo"
}

{ pipe_to_pager_fifo <&3 3<&- & } 3<&0
exec less < "$pager_fifo"
