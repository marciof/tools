#!/bin/sh
# Compresses PDF files, without replacing the original.

# TODO: warn before overwriting

set -e -u

if [ $# -eq 0 ]; then
    set -- *.pdf
fi

for pdf_file; do
    base_name="${pdf_file%.*}"
    compressed_pdf_file="$base_name.pdf.compressed"

    gs -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -sOutputFile="$compressed_pdf_file" "$pdf_file" >&2
    printf '%s\t%s\n' "$pdf_file" "$compressed_pdf_file"
done
