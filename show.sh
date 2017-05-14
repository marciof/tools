#!/bin/sh
set -e -u

status_cant_execute=126
arg_separator="$(printf "\036")" # ASCII RS

disable_mode_opt=d
help_opt=h
mode_option_opt=p

mode_description_dir='list directories via `ls`'
mode_description_file='read files'
mode_description_stdin='read standard input'
mode_description_vcs='show VCS revisions via `git`'

mode_options_dir=
mode_options_file=
mode_options_stdin=
mode_options_vcs=

mode_run_dir() {
    if [ -d "$1" ]; then
        run_with_mode_options "$mode_options_dir" "$1" pty ls
    else
        return $status_cant_execute
    fi
}

mode_run_file() {
    if [ -e "$1" -a ! -d "$1" ]; then
        run_with_mode_options "$mode_options_file" "$1" cat
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

mode_run_vcs() {
    if git --no-pager rev-parse --quiet --verify "$1" 2>/dev/null; then
        run_with_mode_options "$mode_options_vcs" "$1" pty git --no-pager show
    else
        return $status_cant_execute
    fi
}

assert_mode_exists() {
    if ! type "mode_run_$1" >/dev/null; then
        echo "$1: no such mode" >&2
        return 1
    else
        return 0
    fi
}

disable_mode() {
    assert_mode_exists "$1"
    eval "mode_run_$1() { return $status_cant_execute; }"
}

add_mode_option() {
    local name="${1%%=?*}"

    if [ ${#name} -eq ${#1} -o ${#name} -eq 0 ]; then
        echo "$1: missing mode name/option" >&2
        return 1
    fi

    assert_mode_exists "$name"
    local option="${1#?*=}"
    local current="$(var "mode_options_$name")"

    export "mode_options_$name=$current${current:+$arg_separator}$option"
    return 0
}

run_with_mode_options() {
    local options="$1"
    local input="$2"
    shift 2

    if [ -z "$options" ]; then
        "$@" "$input"
    else
        printf "%s" "$options${options:+$arg_separator}$input" \
            | tr "$arg_separator" '\0' \
            | xargs -0 -- "$@"
    fi
}

print_usage() {
    local mode

    cat <<USAGE
Usage: $(basename "$0") [OPTION]... [INPUT]...

Options:
  -$help_opt           display this help and exit
  -$disable_mode_opt NAME      disable a mode
  -$mode_option_opt NAME=OPT  pass an option to a mode

Modes:
USAGE

    for mode in stdin file dir vcs; do
        printf "  %-13s%s\n" "$mode" "$(var "mode_description_$mode")"
    done
}

process_options() {
    local option

    while getopts "$disable_mode_opt:$help_opt$mode_option_opt:" option "$@"; do
        case "$option" in
            "$disable_mode_opt")
                disable_mode "$OPTARG"
                ;;
            "$help_opt")
                print_usage
                exit 0
                ;;
            "$mode_option_opt")
                add_mode_option "$OPTARG"
                ;;
            ?)
                echo "Try '-$help_opt' for more information." >&2
                return 1
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
    for mode in file dir vcs; do
        if "mode_run_$mode" "$input"; then
            continue 2
        fi
    done

    echo "$input: Unsupported input" >&2
    exit 1
done

exit 0
