#!/bin/bash

# https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html
set -o nounset

# Abort when shell isn't interactive.
# https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_05_02
case "$-" in *i*) ;; *) return 0;; esac

# Arguments: <command> ...
# Returns:
#   0 if at least one command was found
#   1 if no command was found
# Env:
#   get DESC = optional command description
#   set HAVE_NAME = which command was found
#   set HAVE_PATH = path to command
have_() {
    for HAVE_NAME; do
        HAVE_PATH="$(command -v "$HAVE_NAME")"
        if [ -n "$HAVE_PATH" ]; then
            return 0
        fi
    done

    echo "* Missing: $* ${DESC:-}" >&2
    return 1
}

# https://www.gnu.org/software/bash/manual/html_node/Bash-Variables.html#index-BASH_005fSOURCE
# shellcheck disable=SC3028,SC3054
self_file="${BASH_SOURCE[0]}"

cache_file="$self_file-cache"

for sub_aliases in "$self_file".*; do
    # shellcheck disable=SC1090
    if [ -r "$sub_aliases" ] && . "$sub_aliases"; then
        echo "* Loaded: ${sub_aliases##"$HOME/"}" >&2
    fi
done

# https://www.gnu.org/software/bash/manual/html_node/The-Shopt-Builtin.html
# shellcheck disable=SC3044
shopt -s autocd dirspell histappend

# https://www.gnu.org/software/bash/manual/html_node/Bash-Variables.html#index-HISTCONTROL
export HISTCONTROL=ignoredups

# https://www.gnu.org/software/bash/manual/html_node/Bash-Variables.html#index-PROMPT_005fDIRTRIM
export PROMPT_DIRTRIM=2

# https://www.gnu.org/software/coreutils/manual/html_node/dircolors-invocation.html
have_ dircolors && eval "$("$HAVE_NAME" --sh)"

have_ lesspipe lesspipe.sh && eval "$("$HAVE_NAME")"
export LESS='--tabs=4 --clear-screen --LONG-PROMPT --RAW-CONTROL-CHARS --ignore-case'

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
export PYTHONDONTWRITEBYTECODE=x

# Disable XON/XOFF flow control so that Ctrl+S can be used for
# `bind -q forward-search-history`.
# https://www.gnu.org/software/coreutils/manual/html_node/Input.html#index-ixon
# https://www.gnu.org/software/bash/manual/html_node/Commands-For-History.html#index-forward_002dsearch_002dhistory-_0028C_002ds_0029
stty -ixon

# https://www.gnu.org/software/bash/manual/html_node/Readline-Init-File-Syntax.html#index-completion_002dignore_002dcase
bind 'set completion-ignore-case on'

# https://www.gnu.org/software/bash/manual/html_node/Readline-Init-File-Syntax.html#index-mark_002dsymlinked_002ddirectories
bind 'set mark-symlinked-directories on'

# https://www.gnu.org/software/bash/manual/html_node/Readline-Init-File-Syntax.html#index-visible_002dstats
bind 'set visible-stats on'

# Bind Ctrl-Right as well.
# https://www.gnu.org/software/bash/manual/html_node/Commands-For-Moving.html#index-forward_002dword-_0028M_002df_0029
bind '"\e[1;5C": forward-word'

# Bind Ctrl-Left as well.
# https://www.gnu.org/software/bash/manual/html_node/Commands-For-Moving.html#index-backward_002dword-_0028M_002db_0029
bind '"\e[1;5D": backward-word'

# Bind Ctrl-Delete as well.
# https://www.gnu.org/software/bash/manual/html_node/Commands-For-Killing.html#index-kill_002dword-_0028M_002dd_0029
bind '"\e[3;5~": kill-word'

no_color='\[\e[0m\]'
blue_bold='\[\e[1;34m\]'
yellow='\[\e[0;33m\]'

# https://www.gnu.org/software/bash/manual/html_node/Controlling-the-Prompt.html
custom_ps1="$blue_bold\w$no_color"

# https://man.openbsd.org/ssh#SSH_CONNECTION
if [ -n "${SSH_CONNECTION:-}" ]; then
    # https://www.gnu.org/software/bash/manual/html_node/Controlling-the-Prompt.html
    custom_ps1="$yellow\\u@\\h$no_color $custom_ps1"
fi

alias -- -='cd -'
alias j='jobs -l'

if DESC='<https://www.nano-editor.org>' have_ nano; then
    alias nano='nano -Sw'
    export EDITOR="$HAVE_NAME"
fi

if DESC='<https://github.com/andreafrancia/trash-cli>' have_ trash-put; then
    # shellcheck disable=SC2139
    alias r="$HAVE_NAME --"
fi

if DESC='<https://github.com/sharkdp/fd>' have_ fd fdfind; then
    # shellcheck disable=SC2139
    alias fd="$HAVE_NAME"
fi

if DESC='<https://www.freedesktop.org/wiki/Software/xdg-utils/>' have_ xdg-open; then
    # shellcheck disable=SC2139
    alias o="$HAVE_NAME"
fi

if have_ show.sh; then
    # shellcheck disable=SC2139
    alias s="$HAVE_NAME -t ls=-Fh -t ls=--group-directories-first -t ls=--dereference-command-line-symlink-to-dir"
    export PAGER="$HAVE_PATH"
fi

# Arguments: [text to copy] ...
#   OR
# Stdin: text to copy
if DESC='<https://github.com/bugaevc/wl-clipboard>' have_ wl-copy; then
    # shellcheck disable=SC2139
    alias cb="$HAVE_NAME --"
elif DESC='<https://github.com/astrand/xclip>' have_ xclip; then
    cb() {
        if [ $# -gt 0 ]; then
            printf %s "$*" | xclip -selection clip-board
        else
            xclip -selection clip-board
        fi
    }
fi

# FIXME have `ag` honor the `$PAGER` env var
if DESC='<https://github.com/ggreer/the_silver_searcher>' have_ ag; then
    if [ -n "${PAGER:-}" ]; then
        # shellcheck disable=SC2139
        alias f="$HAVE_NAME --follow --pager \"$PAGER\""
    else
        # shellcheck disable=SC2139
        alias f="$HAVE_NAME --follow"
    fi
fi

# FIXME move to its own Git-specific sub-aliases file?
if DESC='<https://git-scm.com>' have_ git; then
    # FIXME document
    c() {
        _c_num_cached=$(git diff --cached --name-only | wc -l)

        if  [ $# -eq 0 ] && [ "$_c_num_cached" -eq 0 ]; then
            git commit -a
        else
            git commit "$@"
        fi
    }

    alias g=git

    # https://git-scm.com/docs
    alias a='g add'
    alias b='g branch -vv'
    alias d='g diff'
    alias h='g blame --date=short'
    alias k='g checkout'
    alias l='g log --graph --pretty="tformat:%C(yellow)%h%C(reset) -- %s %C(green)%ai %C(cyan)%aN%C(blue bold)%d"'
    alias p='g push'
    alias t='g status'
    alias u='g pull'

    # FIXME `_completion_loader` was deprecated in v2.12
    #   https://github.com/scop/bash-completion/commit/d9082d2c8dff6b709786862bcd1b8d1698648ea1
    if DESC='<https://github.com/scop/bash-completion>' have_ _completion_loader; then
        "$HAVE_NAME" git

        __git_complete g __git_main
        __git_complete a _git_add
        __git_complete b _git_branch
        __git_complete c _git_commit
        __git_complete d _git_diff
        __git_complete h __gitcomp
        __git_complete k _git_checkout
        __git_complete l _git_log
        __git_complete p _git_push
        __git_complete t _git_status
        __git_complete u _git_pull
    fi

    if [ ! -e "$cache_file" ]; then
        git_commit_template_file="$cache_file-git-commit-template"
        echo >"$git_commit_template_file"

        git config --global commit.template "$git_commit_template_file"
        git config --global pager.status true

        case "$(git help config 2>&1)" in
            *--rebase-merges*)
                git config --global pull.rebase merges;;
            *--preserve-merges*)
                git config --global pull.rebase preserve;;
            *)
                git config --global --bool pull.rebase true;;
        esac
    fi

    export GIT_PS1_SHOWSTASHSTATE=x
    export GIT_PS1_STATESEPARATOR=
    export GIT_EDITOR="${EDITOR:-}"
    export GIT_PAGER="${PAGER:-}"

    if ! command -v __git_ps1 >/dev/null; then
        echo '* Missing: git prompt: https://github.com/git/git/blob/master/contrib/completion/git-prompt.sh' >&2
    else
        green='\[\e[0;32m\]'
        custom_ps1="$custom_ps1$green\$(__git_ps1 ' %s')$no_color"
    fi
fi

job_count_ps1_() {
    local jobs
    jobs=$(jobs -p -r -s | wc -l)
    [ "$jobs" -gt 0 ] && echo " $jobs"
}

# FIXME include job count visual formatting in its function
red_bold='\[\e[1;31m\]'

# FIXME show $? if non-zero from previous command?
export PS1="$custom_ps1$red_bold\$(job_count_ps1_)$no_color\\$ "

: >"$cache_file"
