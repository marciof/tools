#!/bin/sh
set -e -u

disable_mode_opt=d
help_opt=h
mode_opt=p

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

    set -- "$@" '' ls

    if [ -n "$is_tty_out" ]; then
        set -- "$@" -C --color=always
    fi

    run_with_mode_options "$mode_options_dir" "$@"
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

    _pager_buffer_file="$(mktemp)"
    trap "rm $_pager_buffer_file" EXIT

    _pager_buffer_len=0
    _pager_buffer_max_len="$(($(tput lines) / 2))"

    # Can't use `head` here since it causes `git` to stop output abruptly.
    while IFS= read -r buffered_line; do
        _pager_buffer_len=$((_pager_buffer_len + 1))
        printf '%s\n' "$buffered_line" >>"$_pager_buffer_file"

        if [ "$_pager_buffer_len" -ge "$_pager_buffer_max_len" ]; then
            break
        fi
    done

    unset _pager_num_buffer_lines _pager_max_buffer_lines

    if ! IFS= read -r buffered_line; then
        cat "$_pager_buffer_file"
        exit "$?"
    fi

    printf '%s\n' "$buffered_line" >>"$_pager_buffer_file"
    _pager_fifo="$(mktemp -u)"
    trap "rm $_pager_fifo" EXIT
    mkfifo "$_pager_fifo"

    { cat "$_pager_buffer_file" - >"$_pager_fifo" <&3 3<&- & } 3<&0
    run_with_mode_options "$mode_options_pager" - Y less <"$_pager_fifo"
    unset _pager_buffer_file _pager_fifo
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

    set -- "$@" '' git --no-pager show

    if [ -n "$is_tty_out" ]; then
        set -- "$@" --color=always
    fi

    run_with_mode_options "$mode_options_vcs" "$@"
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
    _add_opt_name="${1%%=?*}"

    if [ ${#_add_opt_name} -eq ${#1} -o ${#_add_opt_name} -eq 0 ]; then
        echo "$1: missing mode name/option" >&2
        unset _add_opt_name
        return 1
    fi

    assert_mode_exists "$_add_opt_name"
    _add_opt_option="${1#?*=}"
    _add_opt_current="$(var "mode_options_$_add_opt_name")"

    export "mode_options_$_add_opt_name=$_add_opt_current${_add_opt_current:+$arg_var_separator}$_add_opt_option"
    unset _add_opt_name _add_opt_option _add_opt_current
    return 0
}

run_with_mode_options() {
    _run_opts="$1"
    _run_input="$2"
    _run_uses_stdin="$3"
    shift 3

    if [ -z "$_run_opts" ]; then
        "$@" "$_run_input"
    elif [ -z "$_run_uses_stdin" ]; then
        printf %s "$_run_opts${_run_opts:+$arg_var_separator}$_run_input" \
            | xargs -d "$arg_var_separator" -- "$@"
    else
        _run_args_file="$(mktemp)"
        trap "rm $_run_args_file" EXIT

        printf %s "$_run_opts${_run_opts:+$arg_var_separator}$_run_input" \
            >"$_run_args_file"
        xargs -a "$_run_args_file" -d "$arg_var_separator" -- "$@"
        unset _run_args_file
    fi

    unset _run_options _run_input _run_uses_stdin
}

print_usage() {
    cat <<USAGE
Usage: $(basename "$0") [OPTION]... [INPUT]...

Options:
  -$help_opt           display this help and exit
  -$disable_mode_opt NAME      disable a mode
  -$mode_opt NAME=OPT  pass an option to a mode

Mode:
USAGE

    for _help_mode in stdin file dir vcs pager; do
        if ! type "mode_can_$_help_mode" >/dev/null 2>&1 \
            || "mode_can_$_help_mode"
        then
            _help_has=' '
        else
            _help_has=x
        fi

        printf '%c %-13s%s%s\n' "$_help_has" "$_help_mode" \
            "$(var "mode_description_$_help_mode")"
    done

    unset _help_mode _help_has
}

process_options() {
    while getopts "$disable_mode_opt:$help_opt$mode_opt:" _getopt_opt "$@"; do
        case "$_getopt_opt" in
            "$disable_mode_opt")
                disable_mode "$OPTARG"
                ;;
            "$help_opt")
                print_usage
                exit 0
                ;;
            "$mode_opt")
                add_mode_option "$OPTARG"
                ;;
            ?)
                echo "Try '-$help_opt' for more information." >&2
                unset _getopt_opt
                return 1
                ;;
        esac
    done

    unset _getopt_opt
}

run_input_modes() {
    if ! mode_run_stdin && [ $# -eq 0 ]; then
        set -- .
    fi

    for _run_all_input; do
        for _run_all_mode in file dir vcs; do
            if "mode_run_$_run_all_mode" "$_run_all_input"; then
                continue 2
            fi
        done

        echo "$_run_all_input: unsupported input" >&2
        unset _run_all_input _run_all_mode
        return 1
    done

    unset _run_all_input _run_all_mode
    return 0
}

var() {
    eval echo "\$$1"
}

process_options "$@"
shift $((OPTIND - 1))
run_input_modes "$@" | { mode_run_pager || cat; }
