#!/bin/sh

# Compresses PDF files, without replacing the original.
#
# If no PDF files are specified in the command line, then the glob pattern
# '*.pdf' is used instead.
# The compressed PDF file is stored in the same location as the original,
# with its filename ending in ".compressed".
#
# Arguments: [file ...]
# Stdin: none
# Stdout: tab separated lines, one per PDF filename: original, compressed
# Stderr: compression status/progress
#
# Runtime dependencies:
#   apt install ghostscript # Version: 9.52~dfsg-1ubuntu2 # compress PDF
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

if [ $# -eq 0 ]; then
    set -- *.pdf
fi

for pdf_file; do
    compressed_pdf_file="$pdf_file.compressed"

    gs -dNOPAUSE -dBATCH \
        -sDEVICE=pdfwrite \
        -dCompatibilityLevel=1.4 \
        -dPDFSETTINGS=/screen \
        -sOutputFile="$compressed_pdf_file" \
        "$pdf_file" >&2

    original_size="$(stat -c %s "$pdf_file")"
    compressed_size="$(stat -c %s "$compressed_pdf_file")"

    # TODO write to temporary file first, then move
    # TODO don't overwrite
    if [ "$compressed_size" -lt "$original_size" ]; then
        printf '%s\t%s\n' "$pdf_file" "$compressed_pdf_file"
    else
        echo 'Compressed file is larger than original, removing.' >&2
        rm -- "$compressed_pdf_file"
    fi
done
