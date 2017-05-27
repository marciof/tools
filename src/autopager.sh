#!/bin/sh
set -e -u

buffer_file="$(mktemp -t autopager.buffer.XXXXXXXXXX)"
trap 'rm "$buffer_file"' EXIT

nr_buffered_lines=0
max_nr_buffered_lines="$(($(tput lines) / 2))"

# Can't use `head` here since it causes `git` to stop output abruptly.
while IFS= read -r buffered_line; do
    nr_buffered_lines=$((nr_buffered_lines + 1))
    printf '%s\n' "$buffered_line" >>"$buffer_file"

    if [ "$nr_buffered_lines" -ge "$max_nr_buffered_lines" ]; then
        break
    fi
done

if ! IFS= read -r buffered_line; then
    cat "$buffer_file"
    exit "$?"
fi

printf '%s\n' "$buffered_line" >>"$buffer_file"
pager_fifo="$(mktemp -t -u autopager.fifo.XXXXXXXXXX)"
mkfifo "$pager_fifo"

pipe_to_pager_fifo() {
    trap 'rm "$pager_fifo"' EXIT
    cat "$buffer_file" - >"$pager_fifo"
}

{ pipe_to_pager_fifo <&3 3<&- & } 3<&0
less "$@" <"$pager_fifo"
