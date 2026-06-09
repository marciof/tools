#!/bin/sh

# Compresses PDF files.
#
# If no files are specified, then the glob pattern `*.pdf` is used instead.
#
# The compressed file is stored in the same location as the original file, with
# its filename ending in `.compressed.pdf`, unless its size is larger.
# If `trash-put` is available and the size of the compressed file is smaller,
# then the original file is moved to the trash, and the compressed file is
# renamed to the original.
#
# Arguments: [file | directory] ...
#
# Dependencies (runtime): ghostscript
# Dependencies (runtime / optional): trash-cli
# Dependencies (test): shellcheck

set -o errexit -o nounset -o xtrace

# Arguments: <original file> <compressed file>
if command -v trash-put >/dev/null; then
    trash_or_log() {
        echo "Moving original PDF to trash: $1"
        trash-put -- "$1"
        echo "Renaming compressed PDF: $2"
        mv --no-clobber -- "$2" "$1"
    }
else
    trash_or_log() {
        printf '%s\t%s\n' "$1" "$2"
    }
fi

# Arguments: [file | directory]
compress_pdf_files() {
    for pdf_file; do
        if [ -d "$pdf_file" ]; then
            compress_pdf_files "$pdf_file/"*.pdf
            continue
        elif [ ! -r "$pdf_file" ]; then
            echo "PDF not available or not readable: $pdf_file"
            continue
        fi

        # Make sure the new file ends in `.pdf`. Some Ghostscript versions
        # make it an error otherwise due to `-dSAFE` by default.
        compressed_pdf_file="${pdf_file%.pdf}.compressed.pdf"

        ghostscript \
            -dNOPAUSE \
            -sDEVICE=pdfwrite \
            -dPDFSETTINGS=/screen \
            -sOutputFile="$compressed_pdf_file" \
            -- \
            "$pdf_file"

        original_size="$(stat --format %s -- "$pdf_file")"
        compressed_size="$(stat --format %s -- "$compressed_pdf_file")"

        if [ "$compressed_size" -ge "$original_size" ]; then
            echo "Compressed PDF is larger, removing: $compressed_pdf_file"
            rm -- "$compressed_pdf_file"
        else
            trash_or_log "$pdf_file" "$compressed_pdf_file"
        fi
    done
}

if [ $# -eq 0 ]; then
    set -- *.pdf
fi

compress_pdf_files "$@"
