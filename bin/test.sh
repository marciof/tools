#!/bin/sh

for test_file; do
    export TESTDIR="$(dirname "$test_file")"

    cat "$test_file" \
        | sed -E '/^  /! s/^/#/' \
        | sed -E 's/^  \$ //' \
        | grep -v -E '^  ' \
        | sed -E '/^#/! s/^(.+)$/cat <<"EOT"\n  $ \1\nEOT\ncat <<EOT | sh | sed -E "s:^:  :"\n\1\nEOT/' \
        | sed -E 's/^#(.*)$/cat <<"EOT"\n\1\nEOT/'
done
