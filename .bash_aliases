#!/bin/bash

if ! echo "$-" | grep -q i; then
    return 0
fi

_have() {
    for NAME; do
        if command -v "$NAME" >/dev/null; then
            return 0
        fi
    done

    echo "* Missing: $@" >&2
    return 1
}

child_dir="$(readlink -e "$(dirname "$BASH_SOURCE")")"
abs_home="$(readlink -e ~)"
is_child_home=N

if [ "$child_dir" = "$abs_home" ]; then
    is_child_home=Y
fi

for child in $(ls -1 "$BASH_SOURCE".* 2>/dev/null); do
    . "$child_dir/$(basename "$child")"

    if [ "$is_child_home" = Y ]; then
        child="~/${child##$abs_home/}"
    fi

    echo "* Loaded: $child" >&2
done

shopt -s autocd dirspell histappend
alias -- -='cd -'
alias ..='cd ..'

_have fd
_have dircolors && eval "$($NAME -b)"
_have lesspipe && eval "$($NAME)"

export HISTCONTROL=ignoredups
export LESS='--tabs=4 --clear-screen --LONG-PROMPT --RAW-CONTROL-CHARS --ignore-case'
export PROMPT_DIRTRIM=2
export PYTHONDONTWRITEBYTECODE=x

# Color man pages.
export LESS_TERMCAP_mb=$'\e[1;31m' # begin bold
export LESS_TERMCAP_md=$'\e[1;33m' # begin blink
export LESS_TERMCAP_so=$'\e[01;44;37m' # begin reverse video
export LESS_TERMCAP_us=$'\e[01;37m' # begin underline
export LESS_TERMCAP_me=$'\e[0m' # reset bold/blink
export LESS_TERMCAP_se=$'\e[0m' # reset reverse video
export LESS_TERMCAP_ue=$'\e[0m' # reset underline

stty -ixon # Allow `bind -q forward-search-history`.

bind 'set bind-tty-special-chars Off'
bind 'set completion-ignore-case On'
bind 'set expand-tilde Off'
bind 'set mark-symlinked-directories On'
bind 'set visible-stats On'

bind '"\e[1;5C": forward-word' # ctrl-right
bind '"\e[1;5D": backward-word' # ctrl-left
bind '"\e[3;5~": kill-word' # ctrl-delete

_color_off='\e[0m'
_yellow='\e[0;33m'

if [ -n "$BASHRC_CUSTOM_LOCATION" ]; then
    _host_prompt=" \[$_yellow\]$BASHRC_CUSTOM_LOCATION\[$_color_off\]"
elif [ -n "$SSH_CLIENT" -o -n "$SSH_TTY" ]; then
    _host_prompt=" \[$_yellow\]\\u@\\h\[$_color_off\]"
else
    _host_prompt=
fi

if _have nano; then
    alias nano='nano -Sw'
    export EDITOR="$NAME" GIT_EDITOR="$NAME"
fi

if _have show.sh; then
    alias s="$NAME -p dir=-Fh -p dir=--group-directories-first -p dir=--dereference-command-line-symlink-to-dir"
    export PAGER="$NAME" GIT_PAGER="$NAME"
fi

if _have ag; then
    if [ -n "$PAGER" ]; then
        alias f="$NAME --follow --hidden --pager \"$PAGER\""
    else
        alias f="$NAME --follow --hidden"
    fi
fi

if _have git; then
    _load_git_completions() {
        if command -v _completion_loader >/dev/null; then
            _completion_loader git
        fi

        if ! command -v __git_complete >/dev/null; then
            printf "\n* Missing: bash-completion for Git\n" >&2
            return
        fi

        __git_complete a _git_add
        __git_complete b _git_branch
        __git_complete c _git_commit
        __git_complete d _git_diff
        __git_complete h __gitcomp
        __git_complete l _git_log
        __git_complete p _git_push
        __git_complete r _git_checkout
        __git_complete t _git_status
        __git_complete v _git_pull

        unset -f _load_git_completions
    }

    c() {
        local cached=$(git diff --cached --name-only | wc -l)

        if  [ $# -eq 0 -a $cached -eq 0 ]; then
            git commit -a
        else
            git commit "$@"
        fi
    }

    alias a='git add "$@"'
    alias b='git branch -vv "$@"'
    alias d='git diff "$@"'
    alias h='git blame --date=short "$@"'
    alias l='git log --graph --pretty="tformat:%C(yellow)%h%C(reset) -- %s %C(green)%ai %C(cyan)%aN%C(blue bold)%d" "$@"'
    alias p='git push "$@"'
    alias r='git checkout "$@"'
    alias t='git status "$@"'
    alias v='git pull "$@"'

    git config --global pull.rebase preserve

    export GIT_PS1_SHOWSTASHSTATE=x
    export GIT_PS1_STATESEPARATOR=

    for ALIAS in a b c d h l p r t v; do
        eval "_${ALIAS}() { _load_git_completions; }"
        eval "complete -F _$ALIAS $ALIAS"
    done

    if ! command -v __git_ps1 >/dev/null; then
        echo "* Missing: https://github.com/git/git/blob/master/contrib/completion/git-prompt.sh" >&2
    else
        _git_prompt="\[\e[0;32m\]\$(__git_ps1 ' %s')\[$_color_off\]"
    fi
fi

_job_count_ps1() {
    local jobs=$(jobs -p -r -s | wc -l)
    [ $jobs -gt 0 ] && echo " $jobs"
}

if [ -z "$BASHRC_KEEP_PROMPT" ]; then
    export PS1="\[\e[1;34m\]\w\[$_color_off\]$_host_prompt$_git_prompt\[\e[1;31m\]\$(_job_count_ps1)\[$_color_off\]\\$ "
fi

unset -f _have
