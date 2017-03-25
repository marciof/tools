#!/bin/sh
set -e -u

buffer_file="$(mktemp)"
trap 'rm "$buffer_file"' EXIT

nr_buffered_lines=0
max_nr_lines="$(($(tput lines) / 2))"

# Can't use `head` here since it causes `git` to stop output abruptly.
while IFS= read -r buffered_line; do
    nr_buffered_lines=$((nr_buffered_lines + 1))
    echo "$buffered_line" >>"$buffer_file"

    if [ "$nr_buffered_lines" -ge "$max_nr_lines" ]; then
        break
    fi
done

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

# Use `exec` on the pager to correctly receive signals.
{ pipe_to_pager_fifo <&3 3<&- & } 3<&0
exec less < "$pager_fifo"
