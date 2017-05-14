#!/bin/sh
set -e -u

status_cant_execute=126
arg_separator="$(printf '\036')" # ASCII RS
pty="${SHOW_PTY:-pty}"

disable_plugin_opt=d
help_opt=h
plugin_option_opt=p

plugin_description_dir='list directories via `ls`, cwd by default'
plugin_description_file='read files'
plugin_description_stdin='read standard input, by default'
plugin_description_vcs='show VCS revisions via `git`, HEAD by default'

plugin_options_dir=
plugin_options_file=
plugin_options_stdin=
plugin_options_vcs=

plugin_run_dir() {
    if [ -d "$1" ]; then
        run_with_plugin_options "$plugin_options_dir" "$1" $pty ls
    else
        return "$status_cant_execute"
    fi
}

plugin_run_file() {
    if [ -e "$1" -a ! -d "$1" ]; then
        run_with_plugin_options "$plugin_options_file" "$1" cat
    else
        return "$status_cant_execute"
    fi
}

plugin_run_stdin() {
    if [ ! -t 0 ]; then
        cat
    else
        return "$status_cant_execute"
    fi
}

plugin_can_vcs() {
    command -v git >/dev/null
}

plugin_run_vcs() {
    if git --no-pager rev-parse --quiet --verify "$1" 2>/dev/null; then
        run_with_plugin_options "$plugin_options_vcs" "$1" $pty git --no-pager show
    else
        return "$status_cant_execute"
    fi
}

assert_plugin_exists() {
    if ! type "plugin_run_$1" >/dev/null; then
        echo "$1: no such plugin" >&2
        return 1
    else
        return 0
    fi
}

disable_plugin() {
    assert_plugin_exists "$1"
    eval "plugin_run_$1() { return $status_cant_execute; }"
}

add_plugin_option() {
    local name="${1%%=?*}"

    if [ ${#name} -eq ${#1} -o ${#name} -eq 0 ]; then
        echo "$1: missing plugin name/option" >&2
        return 1
    fi

    assert_plugin_exists "$name"
    local option="${1#?*=}"
    local current="$(var "plugin_options_$name")"

    export "plugin_options_$name=$current${current:+$arg_separator}$option"
    return 0
}

run_with_plugin_options() {
    local options="$1"
    local input="$2"
    shift 2

    if [ -z "$options" ]; then
        "$@" "$input"
    else
        printf '%s' "$options${options:+$arg_separator}$input" \
            | tr "$arg_separator" '\0' \
            | xargs -0 -- "$@"
    fi
}

print_usage() {
    local plugin
    local unavailable

    cat <<USAGE
Usage: $(basename "$0") [OPTION]... [INPUT]...
Version: 0.12.0

Options:
  -$help_opt           display this help and exit
  -$disable_plugin_opt NAME      disable a plugin
  -$plugin_option_opt NAME=OPT  pass an option to a plugin

Plugins:
USAGE

    for plugin in stdin file dir vcs; do
        if ! type "plugin_can_$plugin" >/dev/null || "plugin_can_$plugin"; then
            availability=' '
        else
            availability='x'
        fi

        printf '%c %-13s%s%s\n' \
            "$availability" "$plugin" "$(var "plugin_description_$plugin")"
    done

    if [ -z "$pty" ]; then
        printf '\nWarning: pty wrapper command not found\n' >&2
    fi
}

process_options() {
    local option

    while getopts "$disable_plugin_opt:$help_opt$plugin_option_opt:" option "$@"; do
        case "$option" in
            "$disable_plugin_opt")
                disable_plugin "$OPTARG"
                ;;
            "$help_opt")
                print_usage
                exit 0
                ;;
            "$plugin_option_opt")
                add_plugin_option "$OPTARG"
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

if ! command -v "$pty" >/dev/null; then
    pty=
fi

process_options "$@"
shift $((OPTIND - 1))

if ! plugin_run_stdin && [ $# -eq 0 ]; then
    set -- .
fi

# FIXME: use `autopager.sh` (keep separate; do only one thing and well)
for input; do
    for plugin in file dir vcs; do
        if "plugin_run_$plugin" "$input"; then
            continue 2
        fi
    done

    echo "$input: Unsupported input" >&2
    exit 1
done

exit 0
