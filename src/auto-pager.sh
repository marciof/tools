#!/bin/sh
set -e -u

buffer_file="$(mktemp)"
trap "rm ${buffer_file}" EXIT
head -n "$(($(tput lines) / 2))" > "$buffer_file"

if ! IFS= read -r line; then
    cat "$buffer_file"
    exit $?
fi

pager_fifo="$(mktemp -u)"
mkfifo "$pager_fifo"
trap "rm ${pager_fifo}" EXIT

less < "$pager_fifo" &

cat "$buffer_file" > "$pager_fifo"
echo "$line" > "$pager_fifo"
cat > "$pager_fifo"
wait
