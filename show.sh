#!/bin/sh
set -e -u

program_path="$0"
help_option=h
status_cant_execute=126

mode_description_dir='list directories via `ls`'
mode_description_file='read files'
mode_description_stdin='read standard input'

mode_run_dir() {
    if [ -d "$1" ]; then
        ls -- "$1"
    else
        return $status_cant_execute
    fi
}

mode_run_file() {
    if [ -e "$1" -a ! -d "$1" ]; then
        cat -- "$1"
    else
        return $status_cant_execute
    fi
}

mode_run_stdin() {
    if [ ! -t 0 ]; then
        cat
    else
        return $status_cant_execute
    fi
}

print_usage() {
    cat <<USAGE
Usage: $(basename "$program_path") [OPTION]... [INPUT]...

Options:
  -$help_option           display this help and exit

Modes:
USAGE

    for mode in stdin file dir; do
        printf "  %-13s%s\n" "$mode" "$(var mode_description_$mode)"
    done
}

process_options() {
    while getopts h option "$@"; do
        case "$option" in
            h)
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

var() {
    eval echo "\$$1"
}

process_options "$@"
shift $((OPTIND - 1))

if ! mode_run_stdin && [ $# -eq 0 ]; then
    set -- .
fi

for input; do
    for mode in file dir; do
        if mode_run_$mode "$input"; then
            continue 2
        fi
    done

    printf "%s: Unsupported input\n" "$input" 2>&1
    exit 1
done

exit 0
