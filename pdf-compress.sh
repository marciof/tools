#!/bin/sh

# Compresses PDF files.
#
# When given a directory, then the glob pattern `*.pdf` is used instead.
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

set -o errexit -o nounset

indent_stdout() {
    sed 's/^/\|   /'
}

# Arguments: <original file> <compressed file>
if command -v trash-put >/dev/null; then
    trash_or_log() {
        trash-put --verbose -- "$1" 2>&1
        mv --no-clobber --verbose -- "$2" "$1"
    }
else
    trash_or_log() {
        printf '+   %s --> %s\n' "$1" "$2" >&2
    }
fi

# Arguments: <file>
compress_pdf_file() {
    # Make sure the new file ends in `.pdf`. Some Ghostscript versions
    # make it an error otherwise due to `-dSAFE` by default.
    compressed_pdf_file="${1%.pdf}.compressed.pdf"

    # Pretty print header output.
    {
        echo "[ ${1##./} ]"
        printf "+%${#1}s+\n" | tr ' ' '-'
    } >&2
    echo

    if ! ghostscript \
            -dNOPAUSE \
            -sDEVICE=pdfwrite \
            -dPDFSETTINGS=/screen \
            -sOutputFile="$compressed_pdf_file" \
            -- \
            "$1" 2>&1
    then
        # Remove leftover file created by Ghostscript even when it fails.
        rm --verbose -- "$compressed_pdf_file"
        return 1
    fi

    original_size="$(stat --format %s -- "$1")"
    compressed_size="$(stat --format %s -- "$compressed_pdf_file")"

    if [ "$compressed_size" -ge "$original_size" ]; then
        echo "+   Compressed PDF is larger, skipping." >&2
        rm --verbose -- "$compressed_pdf_file"
    else
        trash_or_log "$1" "$compressed_pdf_file"
    fi
}

# Arguments: [file | directory] ...
compress_pdf_files() {
    for file_or_dir; do
        if [ -d "$file_or_dir" ]; then
            compress_pdf_files "${file_or_dir%%/}/"*.pdf
        else
            compress_pdf_file "$file_or_dir" | indent_stdout
            echo
        fi
    done
}

compress_pdf_files "$@"
