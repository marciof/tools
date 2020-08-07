#!/bin/sh
# shellcheck disable=SC2039
set -e -u

# TODO: avoid temporary files
# TODO: refactor naming
# TODO: check modes for missing depedencies
# TODO: file://
# TODO: http://
# TODO: intra-line diff: https://github.com/ymattw/ydiff
# TODO: intra-line diff: https://github.com/git/git/tree/master/contrib/diff-highlight
# TODO: fancier diff: https://github.com/so-fancy/diff-so-fancy
# TODO: diff syntax highlighter: https://github.com/dandavison/delta; https://news.ycombinator.com/item?id=22996374
# TODO: images: libcaca, sixel, https://github.com/stefanhaustein/TerminalImageViewer
# TODO: fancier highlighting: https://github.com/willmcgugan/rich
# TODO: tests: functional, performance

# Separates single-string arguments (eg. to `xargs`) using the ASCII RS char.
arg_separator="$(printf '\036')"

disable_mode_opt=d
help_opt=h
tool_option_opt=p
global_tool_option_opt=i
disable_depth_opt=a

global_tool_options=
is_depth_enabled=Y

# shellcheck disable=SC2034,SC2016
mode_help_bin='read binary file, via "lesspipe"'
# shellcheck disable=SC2034,SC2016
mode_help_color='syntax highlighting, via "highlight"'
# shellcheck disable=SC2034,SC2016
mode_help_dir='list directory, via "ls" or "tree" when depth is disabled'
# shellcheck disable=SC2034,SC2016
mode_help_pager='page output as needed, via "less"'
# shellcheck disable=SC2034,SC2016
mode_help_stdin='read standard input, via "cat"'
# shellcheck disable=SC2034,SC2016
mode_help_text='read plain text file, via "cat"'
# shellcheck disable=SC2034,SC2016
mode_help_vcs='show VCS revision, via "git show"'

# shellcheck disable=SC2034,SC2016
tool_help_lesspipe='`lesspipe` or `lesspipe.sh`, https://www.gnu.org/software/less/'
# shellcheck disable=SC2034
tool_help_highlight='http://www.andre-simon.de/doku/highlight/en/highlight.php'
# shellcheck disable=SC2034,SC2016
tool_help_ls='POSIX `ls`'
# shellcheck disable=SC2034
tool_help_tree='http://mama.indstate.edu/users/ice/tree/'
# shellcheck disable=SC2034,SC2016
tool_help_cat='POSIX `cat`'
# shellcheck disable=SC2034
tool_help_less='https://www.gnu.org/software/less/'
# shellcheck disable=SC2034
tool_help_git='https://git-scm.com'

# Set to a non-empty string so that `is_var_non_null` can detect the variable
# as being defined.

tool_options_lesspipe="$arg_separator"
tool_options_highlight="$arg_separator"
tool_options_ls="$arg_separator"
tool_options_tree="$arg_separator"
tool_options_cat="$arg_separator"
tool_options_less="$arg_separator"
tool_options_git="$arg_separator"

if [ -t 1 ]; then
    is_tty_out=Y
else
    is_tty_out=N
fi

tool_has_cat() {
    command -v lesspipe >/dev/null
}

tool_has_git() {
    command -v git >/dev/null
}

tool_has_highlight() {
    command -v highlight >/dev/null
}

tool_has_less() {
    command -v less >/dev/null
}

tool_has_lesspipe() {
    command -v lesspipe >/dev/null || command -v lesspipe.sh >/dev/null
}

tool_has_ls() {
    command -v ls >/dev/null
}

tool_has_tree() {
    command -v tree >/dev/null
}

mode_can_bin() {
    test -e "$1" && test ! -d "$1" && is_file_binary "$1"
}

mode_has_bin() {
    tool_has_lesspipe
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
    PAGER=cat run_with_options "$tool_options_lesspipe" N "$_bin_exec" "$1"
}

mode_can_color() {
    test "$is_tty_out" = Y
}

mode_has_color() {
    tool_has_highlight
}

mode_run_color() {
    run_with_options "$tool_options_highlight" N \
        highlight --force -O ansi "$@" 2>/dev/null
}

mode_can_dir() {
    test -d "$1"
}

mode_has_dir() {
    tool_has_ls || tool_has_tree
}

mode_run_dir() {
    if [ "$is_tty_out" = Y ]; then
        set -- -C "$@"
    fi

    if [ "$is_depth_enabled" = N ] && tool_has_tree; then
        run_with_options "$tool_options_tree" N tree "$@"
    else
        if [ "$is_tty_out" = Y ]; then
            set -- --color=always "$@"
        fi

        run_with_options "$tool_options_ls" N ls "$@"
    fi
}

mode_can_text() {
    test -e "$1" && test ! -d "$1" && ! is_file_binary "$1"
}

mode_has_text() {
    tool_has_cat
}

mode_run_text() {
    if mode_has_color && mode_can_color; then
        run_with_options "$tool_options_cat" N cat "$1" | mode_run_color "$1"
    else
        run_with_options "$tool_options_cat" N cat "$1"
    fi
}

mode_can_pager() {
    test "$is_tty_out" = Y
}

mode_has_pager() {
    tool_has_less
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

    cat "$_pager_buffer" - | run_with_options "$tool_options_less" Y less
    rm "$_pager_buffer"
}

mode_can_stdin() {
    test ! -t 0
}

mode_has_stdin() {
    tool_has_cat
}

mode_run_stdin() {
    if mode_has_color && mode_can_color; then
        run_with_options "$tool_options_cat" Y cat | mode_run_color
    else
        run_with_options "$tool_options_cat" Y cat
    fi
}

mode_can_vcs() {
    git --no-pager rev-parse --quiet --verify "$1" 2>/dev/null
}

mode_has_vcs() {
    tool_has_git
}

mode_run_vcs() {
    if [ "$is_tty_out" = Y ]; then
        set -- --color=always "$@"
    fi

    run_with_options "$tool_options_git" N git --no-pager show "$@"
}

is_file_binary() {
    _is_bin_path="$1"

    if [ -L "$_is_bin_path" ]; then
        _is_bin_path="$(resolve_symlink "$_is_bin_path")"
    fi

    _is_bin_type="$(LC_MESSAGES=C file -i "$_is_bin_path")"
    _is_bin_type="${_is_bin_type#"$_is_bin_path: "}"

    test "$_is_bin_type" = "${_is_bin_type#text/}"
}

resolve_symlink() {
    _symlink_src="$1"
    _symlink_path="$(LC_MESSAGES=C file "$_symlink_src")"
    _symlink_path="${_symlink_path#"$_symlink_src: symbolic link to "}"

    if [ ! -d "$_symlink_src" ]; then
        _symlink_path="$(dirname "$_symlink_src")/$_symlink_path"
    fi

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

assert_tool_exists() {
    if ! is_var_non_null "tool_options_$1"; then
        echo "$1: no such tool" >&2
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

add_tool_option() {
    _add_opt_name="${1%%=?*}"

    if [ ${#_add_opt_name} -eq ${#1} ] || [ ${#_add_opt_name} -eq 0 ]; then
        echo "$1: missing mode name/option" >&2
        return 1
    fi

    _add_opt_option="${1#?*=}"
    add_parsed_tool_option "$_add_opt_name" "$_add_opt_option"
}

add_global_tool_option() {
    global_tool_options="$global_tool_options${global_tool_options:+$arg_separator}$1"
}

add_parsed_tool_option() {
    _add_p_opt_name="$1"
    _add_p_opt_option="$2"

    assert_tool_exists "$_add_p_opt_name"
    _add_p_opt_current="$(var "tool_options_$_add_p_opt_name")"
    _add_p_opt_current=${_add_p_opt_current#$arg_separator}

    export "tool_options_$_add_p_opt_name=$_add_p_opt_current${_add_p_opt_current:+$arg_separator}$_add_p_opt_option"
    return 0
}

run_with_options() {
    _run_opts="${1#$arg_separator}"
    _run_uses_stdin="$2"
    shift 2

    _run_all_opts="$global_tool_options${global_tool_options:+$arg_separator}$_run_opts"

    if [ -z "$_run_all_opts" ]; then
        "$@"
    elif [ "$_run_uses_stdin" = N ]; then
        printf %s "$_run_all_opts" | xargs -d "$arg_separator" -- "$@"
    else
        _run_args_file="$(mktemp)"
        printf %s "$_run_all_opts" >"$_run_args_file"
        xargs -a "$_run_args_file" -d "$arg_separator" -- "$@"
        rm "$_run_args_file"
    fi
}

print_usage() {
    cat <<USAGE
Usage: $(basename "$0") [OPTION]... [INPUT]...

Options:
  -$help_opt           display this help and exit
  -$disable_mode_opt NAME      disable mode "NAME"
  -$tool_option_opt NAME=OPT  pass option "OPT" to tool "NAME"
  -$global_tool_option_opt OPT       pass option "OPT" to all tools
  -$disable_depth_opt           disable depth limitation (mode dependent)

Modes:
USAGE

    for _help_mode in bin color text dir pager stdin vcs; do
        if "mode_has_$_help_mode"; then
            _help_has=' '
        else
            _help_has=x
        fi

        printf '%c %-13s%s%s\n' "$_help_has" "$_help_mode" \
            "$(var "mode_help_$_help_mode")"
    done

    printf '\nTools:\n'

    for _help_tool in cat git highlight less lesspipe ls tree; do
        if "tool_has_$_help_tool"; then
            _help_has=' '
        else
            _help_has=x
        fi

        printf '%c %-13s%s%s\n' "$_help_has" "$_help_tool" \
            "$(var "tool_help_$_help_tool")"
    done

}

process_options() {
    while getopts "$disable_mode_opt:$help_opt$tool_option_opt:$global_tool_option_opt:$disable_depth_opt" _getopt_opt "$@"; do
        case "$_getopt_opt" in
            "$disable_mode_opt")
                disable_mode "$OPTARG"
                ;;
            "$help_opt")
                print_usage
                exit 0
                ;;
            "$tool_option_opt")
                add_tool_option "$OPTARG"
                ;;
            "$global_tool_option_opt")
                add_global_tool_option "$OPTARG"
                ;;
            "$disable_depth_opt")
                is_depth_enabled=N
                ;;
            ?)
                echo "Try '-$help_opt' for more information." >&2
                return 1
                ;;
        esac
    done
}

run_non_paging_modes() {
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

is_var_non_null() {
    if [ "$(eval echo "\${$1:+NON_NULL}")" = NON_NULL ]; then
        return 0
    else
        return 1
    fi
}

var() {
    eval echo "\$$1"
}

process_options "$@"
shift $((OPTIND - 1))

if mode_can_pager; then
    run_non_paging_modes "$@" | mode_run_pager
else
    run_non_paging_modes "$@"
fi
