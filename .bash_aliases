#!/bin/bash

if [ -z "$(echo "$-" | tr -c -d i)" ]; then
    return 0
fi

_have() {
    for NAME; do
        if command -v "$NAME" > /dev/null; then
            return 0
        fi
    done

    echo "* Missing: $@" >&2
    return 1
}

child_dir="$(readlink -e "$(dirname "$BASH_SOURCE")")"

for child in $(ls -1 "$BASH_SOURCE".* 2> /dev/null); do
    source "$child_dir/$(basename "$child")"
    echo "* Loaded: $child" >&2
done

shopt -s autocd dirspell histappend
alias -- -='cd -'
alias ..='cd ..'

_have dircolors && eval "$($NAME -b)"
_have lesspipe && eval "$($NAME)"

export HISTCONTROL=ignoredups
export LESS='--tabs=4 --clear-screen --LONG-PROMPT --RAW-CONTROL-CHARS --ignore-case'
export PATH=$PATH:~/.local/bin
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
fi

if _have micro nano; then
    export EDITOR="$NAME" GIT_EDITOR="$NAME"
fi

if _have show; then
    alias s="$NAME -p dir=-Fh -p dir=--color=auto -p dir=--group-directories-first"
    export PAGER="$NAME"
fi

if _have ag; then
    if [ -n "$PAGER" ]; then
        alias f="$NAME --follow --pager \"$PAGER\""
    else
        alias f="$NAME --follow"
    fi
fi

if _have git; then
    _load_git_completions() {
        if type -t _completion_loader > /dev/null; then
            _completion_loader git
        fi

        __git_complete sa _git_add
        __git_complete sb _git_branch
        __git_complete sc _git_commit
        __git_complete sd _git_diff
        __git_complete sh __gitcomp
        __git_complete sl _git_log
        __git_complete sp _git_push
        __git_complete sr _git_checkout
        __git_complete ss _git_pull
        __git_complete st _git_status
    }

    sc() {
        local cached=$(git diff --cached --name-only | wc -l)

        if  [ $# -eq 0 -a $cached -eq 0 ]; then
            git commit -a
        else
            git commit "$@"
        fi
    }

    alias sa='git add "$@"'
    alias sb='git branch -vv "$@"'
    alias sd='git diff "$@"'
    alias sh='git blame --date=short "$@"'
    alias sl='git log --graph --pretty="tformat:%C(yellow)%h%C(reset) -- %s %C(green)%ai %C(cyan)%aN%C(blue bold)%d" "$@"'
    alias sp='git push "$@"'
    alias sr='git checkout "$@"'
    alias ss='git pull "$@"'
    alias st='git status "$@"'

    git config --global push.default simple
    git config --global branch.autosetuprebase always

    export GIT_PS1_SHOWSTASHSTATE=x
    export GIT_PS1_STATESEPARATOR=

    for ALIAS in sa sb sc sd sh sl sp sr ss st; do
        eval "_${ALIAS}() { _load_git_completions; }"
        eval "complete -F _${ALIAS} ${ALIAS}"
    done

    if ! type -t __git_ps1 > /dev/null; then
        echo "* Missing: https://github.com/git/git/blob/master/contrib/completion/git-prompt.sh" >&2
        alias __git_ps1=:
    fi

    _git_prompt="\[\e[0;32m\]\$(__git_ps1 ' %s')\[$_color_off\]"
fi

_jobs_nr_ps1() {
    local jobs=$(jobs -p | wc -l)
    [ $jobs -gt 0 ] && echo " $jobs"
}

if [ -z "$BASHRC_KEEP_PROMPT" ]; then
    export PS1="\[\e[1;34m\]\w\[$_color_off\]$_host_prompt$_git_prompt\[\e[1;31m\]\$(_jobs_nr_ps1)\[$_color_off\]\\$ "
fi
