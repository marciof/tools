#!/bin/sh
set -e -u

disable_plugin_option=d
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

disable_plugin() {
    if ! type "plugin_run_$1" >/dev/null; then
        echo "$1: no such plugin" 2>&1
        return 1
    else
        eval "plugin_run_$1() { return $status_cant_execute; }"
        return 0
    fi
}

print_usage() {
    local plugin

    cat <<USAGE
Usage: $(basename "$0") [OPTION]... [INPUT]...

Options:
  -$disable_plugin_option NAME      disable a plugin
  -$help_option           display this help and exit

Plugins:
USAGE

    for plugin in stdin file dir; do
        printf "  %-13s%s\n" "$plugin" "$(var "plugin_description_$plugin")"
    done
}

process_options() {
    local option

    while getopts "$disable_plugin_option:$help_option" option "$@"; do
        case "$option" in
            "$disable_plugin_option")
                disable_plugin "$OPTARG"
                ;;
            "$help_option")
                print_usage
                exit 0
                ;;
            ?)
                echo "Try '-$help_option' for more information." 2>&1
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

    echo "$input: Unsupported input" 2>&1
    exit 1
done

exit 0
