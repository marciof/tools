#!/bin/sh
set -e

help_option=h
plugins=dir

dir_plugin_name=dir
dir_plugin_description='list directories via `ls`'

dir_plugin_run() {
    ls "$@"
}

var() {
    eval echo "\$$1"
}

print_usage() {
    printf "$(xargs -0 echo <<USAGE )" "$(basename "$0")" "$help_option"
Usage: %s [OPTION]... [INPUT]...

Options:
  -%s            display this help and exit\n
USAGE

    if [ -n "$plugins" ]; then
        printf "\nPlugins:\n"

        for plugin in $plugins; do
            printf "  %-14s%s\n" \
                "$(var ${plugin}_plugin_name)" \
                "$(var ${plugin}_plugin_description)"
        done
    fi
}

parse_options() {
    while getopts h option "$@"; do
        case "$option" in
            h)
                print_usage
                exit 0
                ;;
            ?)
                printf "Try '-%s' for more information.\n" "$help_option"
                exit 1
                ;;
        esac
    done
}

parse_options "$@"
shift $((OPTIND - 1))
dir_plugin_run "$@"
