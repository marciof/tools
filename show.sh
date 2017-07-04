#!/bin/sh
set -e -u

disable_mode_opt=d
help_opt=h
mode_option_opt=p

mode_description_dir='list directories via `ls`, cwd by default'
mode_description_file='read files via `cat`'
mode_description_pager='page output via `less`, when needed'
mode_description_stdin='read standard input via `cat`'
mode_description_vcs='show VCS revisions via `git`, HEAD by default'

mode_options_dir=
mode_options_file=
mode_options_pager=
mode_options_stdin=
mode_options_vcs=

status_cant_execute=126
arg_var_separator="$(printf '\036')" # ASCII RS

if [ -t 1 ]; then
    is_tty_out=Y
else
    is_tty_out=
fi

mode_run_dir() {
    if [ ! -d "$1" ]; then
        return "$status_cant_execute"
    fi

    local tty_flags=

    if [ -n "$is_tty_out" ]; then
        tty_flags='-C --color=always'
    fi

    run_with_mode_options "$mode_options_dir" "$1" '' ls $tty_flags
}

mode_run_file() {
    if [ -e "$1" -a ! -d "$1" ]; then
        run_with_mode_options "$mode_options_file" "$1" '' cat
    else
        return "$status_cant_execute"
    fi
}

mode_can_pager() {
    command -v less >/dev/null
}

mode_run_pager() {
    if [ -z "$is_tty_out" ]; then
        return "$status_cant_execute"
    fi

    local buffer_file
    buffer_file="$(mktemp)"
    trap "rm $buffer_file" EXIT

    local nr_buffered_lines=0
    local max_nr_buffered_lines="$(($(tput lines) / 2))"

    # Can't use `head` here since it causes `git` to stop output abruptly.
    while IFS= read -r buffered_line; do
        nr_buffered_lines=$((nr_buffered_lines + 1))
        printf '%s\n' "$buffered_line" >>"$buffer_file"

        if [ "$nr_buffered_lines" -ge "$max_nr_buffered_lines" ]; then
            break
        fi
    done

    if ! IFS= read -r buffered_line; then
        cat "$buffer_file"
        exit "$?"
    fi

    printf '%s\n' "$buffered_line" >>"$buffer_file"
    local pager_fifo
    pager_fifo="$(mktemp -u)"
    trap "rm $pager_fifo" EXIT
    mkfifo "$pager_fifo"

    { cat "$buffer_file" - >"$pager_fifo" <&3 3<&- & } 3<&0
    run_with_mode_options "$mode_options_pager" - Y less <"$pager_fifo"
}

mode_run_stdin() {
    if [ ! -t 0 ]; then
        run_with_mode_options "$mode_options_stdin" - Y cat
    else
        return "$status_cant_execute"
    fi
}

mode_can_vcs() {
    command -v git >/dev/null
}

mode_run_vcs() {
    if ! git --no-pager rev-parse --quiet --verify "$1" 2>/dev/null; then
        return "$status_cant_execute"
    fi

    local tty_flags=

    if [ -n "$is_tty_out" ]; then
        tty_flags='--color=always'
    fi

    run_with_mode_options "$mode_options_vcs" "$1" '' \
        git --no-pager show $tty_flags
}

assert_mode_exists() {
    if ! type "mode_run_$1" >/dev/null 2>&1; then
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
    local current
    current="$(var "mode_options_$name")"

    export "mode_options_$name=$current${current:+$arg_var_separator}$option"
    return 0
}

run_with_mode_options() {
    local options="$1"
    local input="$2"
    local uses_stdin="$3"
    shift 3

    if [ -z "$options" ]; then
        "$@" "$input"
    elif [ -z "$uses_stdin" ]; then
        printf %s "$options${options:+$arg_var_separator}$input" \
            | xargs -d "$arg_var_separator" -- "$@"
    else
        local args_file
        args_file="$(mktemp)"
        trap "rm $args_file" EXIT

        printf %s "$options${options:+$arg_var_separator}$input" >"$args_file"
        xargs -a "$args_file" -d "$arg_var_separator" -- "$@"
    fi
}

print_usage() {
    local mode
    local availability

    cat <<USAGE
Usage: $(basename "$0") [OPTION]... [INPUT]...

Options:
  -$help_opt           display this help and exit
  -$disable_mode_opt NAME      disable a mode
  -$mode_option_opt NAME=OPT  pass an option to a mode

Mode:
USAGE

    for mode in stdin file dir vcs pager; do
        if ! type "mode_can_$mode" >/dev/null 2>&1 || "mode_can_$mode"; then
            availability=' '
        else
            availability=x
        fi

        printf '%c %-13s%s%s\n' \
            "$availability" "$mode" "$(var "mode_description_$mode")"
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

run_input_modes() {
    local input
    local mode

    if ! mode_run_stdin && [ $# -eq 0 ]; then
        set -- .
    fi

    for input; do
        for mode in file dir vcs; do
            if "mode_run_$mode" "$input"; then
                continue 2
            fi
        done

        echo "$input: unsupported input" >&2
        return 1
    done

    return 0
}

var() {
    eval echo "\$$1"
}

process_options "$@"
shift $((OPTIND - 1))
run_input_modes "$@" | { mode_run_pager || cat; }
