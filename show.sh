#!/bin/sh
# shellcheck disable=SC2039
set -e -u

arg_var_separator="$(printf '\036')" # ASCII RS char

disable_mode_opt=d
help_opt=h
mode_option_opt=p
input_modes_option_opt=i
no_depth_option_opt=a
is_depth_enabled=Y

# shellcheck disable=SC2034,SC2016
mode_help_bin='read binary file, `lesspipe` or `lesspipe.sh`'
# shellcheck disable=SC2034,SC2016
mode_help_color="syntax highlight, Andre Simon's \`highlight\`"
# shellcheck disable=SC2034,SC2016
mode_help_dir='list directory, `ls` or `tree` with depth disabled (default cwd)'
# shellcheck disable=SC2034,SC2016
mode_help_pager='page output as needed, `less`'
# shellcheck disable=SC2034,SC2016
mode_help_stdin='read standard input, `cat`'
# shellcheck disable=SC2034,SC2016
mode_help_text='read plain text file, `cat`'
# shellcheck disable=SC2034,SC2016
mode_help_vcs='show VCS revision, `git` (default HEAD)'

# TODO: make options dependent on the mode implementation, not the mode itself
# TODO: show separate help section for mode implementations
# TODO: file://
# TODO: HTTP
# TODO: intra-line diff: https://github.com/ymattw/ydiff
# TODO: intra-line diff: https://github.com/git/git/tree/master/contrib/diff-highlight
# TODO: fancier diff: https://github.com/so-fancy/diff-so-fancy
# TODO: diff syntax highlighter: https://github.com/dandavison/delta; https://news.ycombinator.com/item?id=22996374
# TODO: images: libcaca, sixel, https://github.com/stefanhaustein/TerminalImageViewer
# TODO: fancier highlighting: https://github.com/willmcgugan/rich
# TODO: tests: functional, performance

mode_options_bin=
mode_options_color=
mode_options_dir=
mode_options_pager=
mode_options_stdin=
mode_options_text=
mode_options_vcs=

mode_impl_options_lesspipe=
mode_impl_options_highlight=
mode_impl_options_ls=
mode_impl_options_tree=
mode_impl_options_cat=
mode_impl_options_less=
mode_impl_options_git=

if [ -t 1 ]; then
    is_tty_out=Y
else
    is_tty_out=N
fi

mode_can_bin() {
    test -e "$1" && test ! -d "$1" && is_file_binary "$1"
}

mode_has_bin() {
    command -v lesspipe >/dev/null || command -v lesspipe.sh >/dev/null
}

mode_run_bin() {
    if command -v lesspipe >/dev/null; then
        _bin_exec=lesspipe
    elif command -v lesspipe.sh >/dev/null; then
        _bin_exec=lesspipe.sh
    else
        return 1
    fi

    # shellcheck disable=SC2037
    PAGER=cat run_with_mode_options "$mode_options_bin" N "$_bin_exec" "$1"
}

mode_can_color() {
    test "$is_tty_out" = Y
}

mode_has_color() {
    command -v highlight >/dev/null
}

mode_run_color() {
    run_with_mode_options "$mode_options_color" N \
        highlight --force -O ansi "$@" 2>/dev/null
}

mode_can_dir() {
    test -d "$1"
}

mode_has_dir() {
    return 0
}

mode_run_dir() {
    if [ "$is_tty_out" = Y ]; then
        set -- -C "$@"
    fi

    if [ "$is_depth_enabled" = N ] && command -v tree >/dev/null; then
        run_with_mode_options "$mode_impl_options_tree" N tree "$@"
    else
        if [ "$is_tty_out" = Y ]; then
            set -- --color=always "$@"
        fi

        run_with_mode_options "$mode_options_dir" N ls "$@"
    fi
}

mode_can_text() {
    test -e "$1" && test ! -d "$1" && ! is_file_binary "$1"
}

mode_has_text() {
    return 0
}

mode_run_text() {
    if mode_has_color && mode_can_color; then
        run_with_mode_options "$mode_options_text" N cat "$1" \
            | mode_run_color "$1"
    else
        run_with_mode_options "$mode_options_text" N cat "$1"
    fi
}

mode_can_pager() {
    test "$is_tty_out" = Y
}

mode_has_pager() {
    command -v less >/dev/null
}

mode_run_pager() {
    _pager_buffer="$(mktemp)"
    _pager_max_cols="$(tput cols)"
    _pager_max_lines=$(($(tput lines) / 2))
    _pager_max_bytes=$((_pager_max_cols * _pager_max_lines))

    dd bs=1 "count=$_pager_max_bytes" "of=$_pager_buffer" 2>/dev/null
    _pager_lines="$(fold -b -w "$_pager_max_cols" "$_pager_buffer" | wc -l)"

    if [ "$_pager_lines" -le "$_pager_max_lines" ]; then
        cat "$_pager_buffer"
        rm "$_pager_buffer"
        return
    fi

    cat "$_pager_buffer" - | run_with_mode_options "$mode_options_pager" Y less
    rm "$_pager_buffer"
}

mode_can_stdin() {
    test ! -t 0
}

mode_has_stdin() {
    return 0
}

mode_run_stdin() {
    if mode_has_color && mode_can_color; then
        run_with_mode_options "$mode_options_stdin" Y cat | mode_run_color
    else
        run_with_mode_options "$mode_options_stdin" Y cat
    fi
}

mode_can_vcs() {
    git --no-pager rev-parse --quiet --verify "$1" 2>/dev/null
}

mode_has_vcs() {
    command -v git >/dev/null
}

mode_run_vcs() {
    if [ "$is_tty_out" = Y ]; then
        set -- --color=always "$@"
    fi

    run_with_mode_options "$mode_options_vcs" N git --no-pager show "$@"
}

is_file_binary() {
    _is_bin_path="$1"

    if [ -L "$1" ]; then
        _is_bin_path="$(resolve_symlink "$_is_bin_path")"
    fi

    _is_bin_type="$(LC_MESSAGES=C file -i "$_is_bin_path")"
    _is_bin_type="${_is_bin_type#"$_is_bin_path: "}"

    test "$_is_bin_type" = "${_is_bin_type#text/}"
}

resolve_symlink() {
    _symlink_path="$(LC_MESSAGES=C file "$1")"
    _symlink_path="${_symlink_path#"$1: symbolic link to "}"

    if [ -L "$_symlink_path" ]; then
        resolve_symlink "$_symlink_path"
    else
        echo "$_symlink_path"
    fi
}

assert_mode_exists() {
    if ! type "mode_has_$1" >/dev/null 2>&1; then
        echo "$1: no such mode" >&2
        return 1
    else
        return 0
    fi
}

disable_mode() {
    assert_mode_exists "$1"
    eval "mode_can_$1() { return 1; }"
    eval "mode_has_$1() { return 1; }"
    eval "mode_run_$1() { return 1; }"
}

add_mode_option() {
    _add_opt_name="${1%%=?*}"

    if [ ${#_add_opt_name} -eq ${#1} ] || [ ${#_add_opt_name} -eq 0 ]; then
        echo "$1: missing mode name/option" >&2
        return 1
    fi

    _add_opt_option="${1#?*=}"
    add_parsed_mode_option "$_add_opt_name" "$_add_opt_option"
}

add_input_mode_option() {
    for _add_in_opt_mode in text dir vcs; do
        add_parsed_mode_option "$_add_in_opt_mode" "$1"
    done
}

add_parsed_mode_option() {
    _add_p_opt_name="$1"
    _add_p_opt_option="$2"

    assert_mode_exists "$_add_p_opt_name"
    _add_p_opt_current="$(var "mode_options_$_add_p_opt_name")"

    export "mode_options_$_add_p_opt_name=$_add_p_opt_current${_add_p_opt_current:+$arg_var_separator}$_add_p_opt_option"
    return 0
}

run_with_mode_options() {
    _run_opts="$1"
    _run_uses_stdin="$2"
    shift 2

    if [ -z "$_run_opts" ]; then
        "$@"
    elif [ "$_run_uses_stdin" = N ]; then
        printf %s "$_run_opts" | xargs -d "$arg_var_separator" -- "$@"
    else
        _run_args_file="$(mktemp)"
        printf %s "$_run_opts" >"$_run_args_file"
        xargs -a "$_run_args_file" -d "$arg_var_separator" -- "$@"
        rm "$_run_args_file"
    fi
}

print_usage() {
    cat <<USAGE
Usage: $(basename "$0") [OPTION]... [INPUT]...

Options:
  -$help_opt           display this help and exit
  -$disable_mode_opt NAME      disable mode "NAME"
  -$mode_option_opt NAME=OPT  pass option "OPT" to mode "NAME"
  -$input_modes_option_opt OPT       pass option "OPT" to all named input modes
  -$no_depth_option_opt           disable depth (mode dependent)

Mode:
USAGE

    for _help_mode in bin color dir text pager stdin vcs; do
        if ! type "mode_has_$_help_mode" >/dev/null 2>&1 \
            || "mode_has_$_help_mode"
        then
            _help_has=' '
        else
            _help_has=x
        fi

        printf '%c %-13s%s%s\n' "$_help_has" "$_help_mode" \
            "$(var "mode_help_$_help_mode")"
    done
}

process_options() {
    while getopts "$disable_mode_opt:$help_opt$mode_option_opt:$input_modes_option_opt:$no_depth_option_opt" _getopt_opt "$@"; do
        case "$_getopt_opt" in
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
            "$input_modes_option_opt")
                add_input_mode_option "$OPTARG"
                ;;
            "$no_depth_option_opt")
                is_depth_enabled=N
                ;;
            ?)
                echo "Try '-$help_opt' for more information." >&2
                return 1
                ;;
        esac
    done
}

run_named_input_modes() {
    if mode_can_stdin; then
        mode_run_stdin
    elif [ $# -eq 0 ] && mode_has_dir; then
        set -- .
    fi

    for _run_all_input in "$@"; do
        for _run_all_mode in bin text dir vcs; do
            if "mode_can_$_run_all_mode" "$_run_all_input" \
                    && "mode_run_$_run_all_mode" "$_run_all_input"; then
                continue 2
            fi
        done

        echo "$_run_all_input: unsupported input" >&2
        return 1
    done

    return 0
}

var() {
    eval echo "\$$1"
}

process_options "$@"
shift $((OPTIND - 1))

if mode_can_pager; then
    run_named_input_modes "$@" | mode_run_pager
else
    run_named_input_modes "$@"
fi
