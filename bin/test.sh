#!/bin/sh
set -e -u

for test_file; do
    test_dir="$(readlink -e "$(dirname "$test_file")")"
    test_script="$test_dir/$(basename "$test_file" .t).sh"
    test_output="$test_dir/$(basename "$test_file" .t).out"

    cat <<EOT > "$test_script"
#!/bin/sh
set -u
TESTDIR="$test_dir"
EOT

    chmod +x "$test_script"

    sed -E '/^  /! s/^/#/' < "$test_file" \
        | sed -E 's/^  \$ //' \
        | grep -v -E '^  ' \
        | sed -E '/^#/! s/^(.+)$/cat <<"EOT"\n  $ \1\nEOT\ncat <<EOT | sh 2>\&1 | sed -E "s:^:  :"\n\1\nEOT/' \
        | sed -E "s/^#([^\\\$\"\`'();{}-]*)$/echo \1/" \
        | sed -E 's/^#(.*)$/cat <<"EOT"\n\1\nEOT/' >> "$test_script"

    sh "$test_script" > "$test_output"
done
