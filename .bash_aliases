#!/bin/bash

# Abort when shell isn't interactive, eg. `i`.
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

    echo "* Missing: $*${DESC:-}" >&2
    return 1
}

# shellcheck disable=SC3028,SC3054
self_file="${BASH_SOURCE[0]}"
cache_file="$self_file-cache"

for custom_aliases in "$self_file".*; do
    # shellcheck disable=SC1090
    if [ -r "$custom_aliases" ] && . "$custom_aliases"; then
        echo "* Loaded: ${custom_aliases##"$HOME/"}" >&2
    fi
done

shopt -s autocd dirspell histappend
alias -- -='cd -'
alias j='jobs -l'

have_ dircolors && eval "$("$HAVE_NAME" -b)"
have_ lesspipe lesspipe.sh && eval "$("$HAVE_NAME")"

export HISTCONTROL=ignoredups
export LESS='--tabs=4 --clear-screen --LONG-PROMPT --RAW-CONTROL-CHARS --ignore-case'
export PROMPT_DIRTRIM=2
export PYTHONDONTWRITEBYTECODE=x

stty -ixon # Allow `bind -q forward-search-history`.

bind 'set bind-tty-special-chars Off'
bind 'set completion-ignore-case On'
bind 'set expand-tilde Off'
bind 'set mark-symlinked-directories On'
bind 'set visible-stats On'

bind '"\e[1;5C": forward-word' # ctrl-right
bind '"\e[1;5D": backward-word' # ctrl-left
bind '"\e[3;5~": kill-word' # ctrl-delete

no_color='\[\e[0m\]'
yellow='\[\e[0;33m\]'

if [ -n "${BASHRC_CUSTOM_LOCATION:-}" ]; then
    host_prompt="$yellow$BASHRC_CUSTOM_LOCATION$no_color"
elif [ -n "${SSH_CLIENT:-}" ] || [ -n "${SSH_TTY:-}" ]; then
    host_prompt="$yellow\\u@\\h$no_color"
else
    host_prompt=
fi

if have_ nano; then
    alias nano='nano -Sw'
    export EDITOR="$HAVE_NAME" GIT_EDITOR="$HAVE_NAME"
fi

if DESC=' <https://github.com/andreafrancia/trash-cli>' have_ trash-put; then
    # shellcheck disable=SC2139
    alias r="$HAVE_NAME --"
fi

if DESC=' <https://github.com/sharkdp/fd>' have_ fd fdfind; then
    # shellcheck disable=SC2139
    alias fd="$HAVE_NAME"
fi

if DESC=' <https://www.freedesktop.org/wiki/Software/xdg-utils/>' have_ xdg-open; then
    # shellcheck disable=SC2139
    alias o="$HAVE_NAME"
fi

if have_ show.sh; then
    # shellcheck disable=SC2139
    alias s="$HAVE_NAME -t ls=-Fh -t ls=--group-directories-first -t ls=--dereference-command-line-symlink-to-dir"
    export PAGER="$HAVE_PATH" GIT_PAGER="$HAVE_PATH"
fi

if have_ xclip; then
    cb() {
        if [ $# -gt 0 ]; then
            printf %s "$*" | xclip -selection clip-board
        else
            xclip -selection clip-board
        fi
    }
fi

if DESC=' <https://github.com/ggreer/the_silver_searcher>' have_ ag; then
    if [ -n "$PAGER" ]; then
        # shellcheck disable=SC2139
        alias f="$HAVE_NAME --follow --pager \"$PAGER\""
    else
        # shellcheck disable=SC2139
        alias f="$HAVE_NAME --follow"
    fi
fi

if have_ git; then
    c() {
        local cached
        cached=$(git diff --cached --name-only | wc -l)

        if  [ $# -eq 0 ] && [ "$cached" -eq 0 ]; then
            git commit -a
        else
            git commit "$@"
        fi
    }

    alias g=git
    alias a='g add'
    alias b='g branch -vv'
    alias d='g diff'
    alias h='g blame --date=short'
    alias k='g checkout'
    alias l='g log --graph --pretty="tformat:%C(yellow)%h%C(reset) -- %s %C(green)%ai %C(cyan)%aN%C(blue bold)%d"'
    alias p='g push'
    alias t='g status'
    alias u='g pull'

    if command -v _completion_loader >/dev/null; then
        _completion_loader git
    fi

    if ! command -v __git_complete >/dev/null; then
        echo '* Missing: git Bash completion: https://github.com/git/git/blob/master/contrib/completion/git-completion.bash (or apt "bash-completion", or load order in .bashrc)' >&2
    else
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

    if ! command -v __git_ps1 >/dev/null; then
        echo '* Missing: git prompt: https://github.com/git/git/blob/master/contrib/completion/git-prompt.sh' >&2
    else
        green='\[\e[0;32m\]'
        git_prompt="$green\$(__git_ps1 ' %s')$no_color"
    fi
fi

_job_count_ps1() {
    local jobs
    jobs=$(jobs -p -r -s | wc -l)
    [ "$jobs" -gt 0 ] && echo " $jobs"
}

# FIXME show $? if non-zero from previous command?
if [ -z "${BASHRC_KEEP_PROMPT:-}" ]; then
    red_bold='\[\e[1;31m\]'
    blue_bold='\[\e[1;34m\]'

    # FIXME include job count visual formatting in its function
    export PS1="$blue_bold\w$no_color$host_prompt$git_prompt$red_bold\$(_job_count_ps1)$no_color\\$ "
fi

: >"$cache_file"
