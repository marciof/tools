#!/bin/sh
set -e -u

compile_option=c
help_option=h
is_compile_only=0

compile_t_to_sh() {
    test_dir="$1"
    eot_marker="EOT_$(head -c3 < /dev/urandom | od -An -tx1 | tr -d ' ')"

    cat <<EOT
#!/bin/sh
set -u
TESTDIR="$test_dir"
EOT

    sed -E '/^  /! s/^/#/' \
        | sed -E 's/^  \$ //' \
        | grep -v -E '^  ' \
        | sed -E "/^#/! s/^(.+)\$/cat <<'$eot_marker'\n  \$ \1\n$eot_marker\ncat <<$eot_marker | sh 2>\&1 | sed -E 's:^:  :'\n\1\n$eot_marker/" \
        | sed -E "s/^#([^\\\$\"\`'(){}<>;|&-]*)$/echo \1/" \
        | sed -E "s/^#(.*)\$/cat <<'$eot_marker'\n\1\n$eot_marker/"
}

print_usage() {
    cat <<USAGE
Usage: $(basename "$0") [OPTION]... [TEST]...

Options:
USAGE

    printf '  -%-6s%s\n' "$compile_option" 'compile .t to .sh only'
    printf '  -%-6s%s\n' "$help_option" 'display this help and exit'
}

process_options() {
    while getopts "$compile_option$help_option" option "$@"; do
        case "$option" in
            "$compile_option")
                is_compile_only=1
                ;;
            "$help_option")
                print_usage
                exit 0
                ;;
            ?)
                printf "Try '-%s' for more information.\n" "$help_option" 2>&1
                exit 1
                ;;
        esac
    done
}

process_options "$@"
shift $((OPTIND - 1))

for test_file; do
    test_dir="$(readlink -e "$(dirname "$test_file")")"
    test_script="$test_dir/$(basename "$test_file" .t).sh"
    test_output="$test_dir/$(basename "$test_file" .t).out"

    compile_t_to_sh "$test_dir" < "$test_file" > "$test_script"

    if [ $is_compile_only -eq 0 ]; then
        chmod +x "$test_script"
        sh "$test_script" > "$test_output"
    fi
done
