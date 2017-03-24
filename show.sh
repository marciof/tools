#!/bin/sh
set -e -u

help_option=h
status_cant_execute=126

plugin_description_dir='list directories via `ls`'
plugin_description_file='read files'
plugin_description_stdin='read standard input'

plugin_run_dir() {
    if [ ! -d "$1" ]; then
        return $status_cant_execute
    elif [ -t 1 ]; then
        pty ls -- "$1"
    else
        ls -- "$1"
    fi
}

plugin_run_file() {
    if [ ! -d "$1" -a -e "$1" ]; then
        cat -- "$1"
    else
        return $status_cant_execute
    fi
}

plugin_run_stdin() {
    if [ ! -t 0 ]; then
        cat
    else
        return $status_cant_execute
    fi
}

print_usage() {
    local plugin

    cat <<USAGE
Usage: $(basename "$0") [OPTION]... [INPUT]...

Options:
  -$help_option           display this help and exit

Plugins:
USAGE

    for plugin in stdin file dir; do
        printf "  %-13s%s\n" "$plugin" "$(var "plugin_description_$plugin")"
    done
}

process_options() {
    local option

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

if ! plugin_run_stdin && [ $# -eq 0 ]; then
    set -- .
fi

for input; do
    for plugin in file dir; do
        if "plugin_run_$plugin" "$input"; then
            continue 2
        fi
    done

    printf "%s: Unsupported input\n" "$input" 2>&1
    exit 1
done

exit 0
