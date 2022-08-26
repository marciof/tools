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
# Runtime dependencies (required):
#   apt install ghostscript # Version: 9.52~dfsg-1ubuntu2 # compress PDF
#
# Runtime dependencies (optional):
#   apt install trash-cli # Version: 0.17.1.14-5build1 # move PDF to trash
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

if [ $# -eq 0 ]; then
    set -- *.pdf
fi

has_trash_put=N

if command -v trash-put >/dev/null; then
    has_trash_put=Y
fi

for pdf_file; do
    if ! [ -r "$pdf_file" ]; then
        echo "PDF not available or not readable: $pdf_file" >&2
        continue
    fi

    compressed_pdf_file="$pdf_file.compressed"

    (
        set -x
        gs -dNOPAUSE -dBATCH \
            -sDEVICE=pdfwrite \
            -dCompatibilityLevel=1.4 \
            -dPDFSETTINGS=/screen \
            -sOutputFile="$compressed_pdf_file" \
            -- \
            "$pdf_file" >&2
    )

    original_size="$(stat -c %s -- "$pdf_file")"
    compressed_size="$(stat -c %s -- "$compressed_pdf_file")"

    if [ "$compressed_size" -ge "$original_size" ]; then
        echo "Compressed PDF is larger, removing: $compressed_pdf_file" >&2
        (set -x; rm -- "$compressed_pdf_file")
    elif [ "$has_trash_put" = "Y" ]; then
        echo "Moving original PDF to trash: $pdf_file" >&2
        (set -x; trash-put -- "$pdf_file")
        echo "Renaming compressed PDF: $compressed_pdf_file" >&2
        (set -x; mv -n -- "$compressed_pdf_file" "$pdf_file")
    else
        printf '%s\t%s\n' "$pdf_file" "$compressed_pdf_file"
    fi
done
