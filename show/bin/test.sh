#!/bin/sh
# https://bitbucket.org/brodie/cram/

set -e -u

compile_option=c
help_option=h
is_compile_only=

compile_t_to_sh() {
    local test_dir="$1"
    local random_token="$(head -c3 < /dev/urandom | od -An -tx1 | tr -d ' ')"
    local eot="EOT_$random_token"
    local log="LOG_$random_token"
    local print_log="print_log_$random_token"

    cat <<EOT
#!/bin/sh
set -u
TESTDIR="$test_dir"
$log="\$(mktemp)"
trap 'rm "\$$log"' EXIT
alias $print_log='echo "[\$?]" | grep -vF "[0]" >>"\$$log"; sed -E -e "s/^(\s*)$/\1 (esc)/" -e "s/^/  /" "\$$log"'
EOT

    sed -E '/^  /! s/^/#/' \
        | sed -E 's/^  \$ //' \
        | grep -v -E '^  ' \
        | sed -E "/^#/! s/^(.+)\$/cat <<'$eot'\n  \$ \1\n$eot\n{ \1 ;} >\"\$$log\" 2>\&1; $print_log/" \
        | sed -E "s/^#([^\\\$\"\`'(){}<>;|&-]*)$/echo \1/" \
        | sed -E "s/^#(.*)\$/cat <<'$eot'\n\1\n$eot/"
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
    local option

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
                printf "Try '-%s' for more information.\n" "$help_option" >&2
                exit 1
                ;;
        esac
    done
}

run_test() {
    local test_file="$1"
    local test_dir="$(dirname "$test_file")"
    local abs_test_dir="$(readlink -e "$test_dir")"
    local test_script="$(basename "$test_file" .t).sh"
    local test_output="$(basename "$test_file" .t).err"

    compile_t_to_sh "$abs_test_dir" < "$test_file" > "$test_dir/$test_script"
    chmod +x "$test_dir/$test_script"

    if [ -z "$is_compile_only" ]; then
        local test_scratch_dir="$(mktemp -d)"
        cd "$test_scratch_dir"

        if ! "$abs_test_dir/$test_script" > "$abs_test_dir/$test_output"; then
            echo "$test_file: err" >&2
        fi

        cd "$current_dir"
        rm -rf "${test_scratch_dir:?}"

        if diff -u "$test_file" "$test_dir/$test_output"; then
            echo "$test_file: ok"
            rm "$test_dir/$test_script" "$test_dir/$test_output"
        else
            return 1
        fi
    fi

    return 0
}

process_options "$@"
shift $((OPTIND - 1))
current_dir="$(pwd)"
exit_status=0

for test_path; do
    if [ -d "$test_path" ]; then
        for test_file in "${test_path%/}"/*.t; do
            if ! run_test "$test_file"; then
                exit_status=1
            fi
        done
    else
        if ! run_test "$test_path"; then
            exit_status=1
        fi
    fi
done

exit "$exit_status"
