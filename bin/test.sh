#!/bin/sh
set -u

for test_file; do
    test_dir="$(dirname "$test_file")"
    test_script="$test_dir/$(basename "$test_file" .t).sh"

    cat <<EOT > "$test_script"
#!/bin/sh
set -u
TESTDIR="$(readlink -e "$test_dir")"
EOT

    chmod +x "$test_script"

    sed -E '/^  /! s/^/#/' < "$test_file" \
        | sed -E 's/^  \$ //' \
        | grep -v -E '^  ' \
        | sed -E '/^#/! s/^(.+)$/cat <<"EOT"\n  $ \1\nEOT\ncat <<EOT | sh | sed -E "s:^:  :"\n\1\nEOT/' \
        | sed -E "s/^#([^\\\$\"'-]*)$/echo \1/" \
        | sed -E 's/^#(.*)$/cat <<"EOT"\n\1\nEOT/' >> "$test_script"

    echo "$test_script"
    echo ==========
    cat "$test_script"
    echo ----------
done
