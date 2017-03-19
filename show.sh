#!/bin/sh
set -e -u

program_path="$0"
help_option=h
exit_cant_execute=126
plugins='file dir'
plugin_description_dir='list directories via `ls`'
plugin_description_file='read files'

plugin_run_dir() {
    if [ -d "$1" ]; then
        ls -- "$1"
    else
        return $exit_cant_execute
    fi
}

plugin_run_file() {
    if [ -e "$1" -a ! -d "$1" ]; then
        cat -- "$1"
    else
        return $exit_cant_execute
    fi
}

print_usage() {
    cat <<USAGE
Usage: $(basename "$program_path") [OPTION]... [INPUT]...

Options:
  -$help_option           display this help and exit

Plugins:
USAGE

    for plugin in $plugins; do
        printf "  %-13s%s\n" "$plugin" "$(var plugin_description_${plugin})"
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

if [ $# -eq 0 ]; then
    set -- .
fi

for input; do
    for plugin in $plugins; do
        if plugin_run_${plugin} "$input"; then
            continue 2
        fi
    done

    printf "%s: Unsupported input\n" "$input" 2>&1
    exit 1
done

exit 0
