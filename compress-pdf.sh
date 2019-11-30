#!/bin/sh
set -e -u

if [ $# -eq 0 ]; then
    set -- *.pdf
fi

for input_file; do
    file_name="$(basename "$input_file" .pdf)"
    compressed_file="$(mktemp -u -p . "$file_name.compressed.XXX.pdf")"

    gs -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -sOutputFile="$compressed_file" "$input_file" >&2
    echo "$compressed_file"
done
