#!/bin/bash

_warn() {
    echo "* $@" >&2
}

_have() {
    for NAME; do
        LOCATION=$(which $NAME 2> /dev/null)

        if [ -n "$LOCATION" ]; then
            eval "HAVE_$(echo $NAME | tr '[:lower:]-' '[:upper:]_')='$LOCATION'"
            return 0
        fi
    done

    _warn "Missing: $@"
    return 1
}

for bashrc_child in $(ls -1 "$BASH_SOURCE".* 2> /dev/null); do
    source "$bashrc_child"
    _warn "Loaded: $bashrc_child"
done

shopt -s cdspell checkwinsize histappend

alias -- -='cd -'
alias ..='cd ..'
alias ...='cd ../..'

_have dircolors && eval "$($NAME -b)"
_have lesspipe && eval "$($NAME)"

export ANSIBLE_NOCOWS=x
export HISTCONTROL=ignoreboth
export LESS='-x4 -c -M -R -i'
export PROMPT_DIRTRIM=2
export PYTHONDONTWRITEBYTECODE=x

_color_off='\e[0m'
_yellow='\e[0;33m'
_green='\e[0;32m'
_b_red='\e[1;31m'
_b_blue='\e[1;34m'

if [ -z "$BASHRC_HIDE_USER_HOST" -a \( -n "$SSH_CLIENT" -o -n "$SSH_TTY" \) ]; then
    _ps1_user_host="\[$_yellow\]\\u@\\h\[$_color_off\] "
else
    _ps1_user_host=
fi

# Disable XON/XOFF flow control to allow `bind -q forward-search-history`.
stty -ixon

bind 'set bind-tty-special-chars Off'
bind 'set completion-ignore-case On'
bind 'set expand-tilde Off'
bind 'set mark-symlinked-directories On'
bind 'set visible-stats On'

bind '"\e[1;5C": forward-word'                  # Ctrl + Right
bind '"\e[1;5D": backward-word'                 # Ctrl + Left
bind '"\e[3;5~": kill-word'                     # Ctrl + Delete
bind '"\e[2;5~": backward-kill-word'            # Ctrl + Insert
bind '"\e[2~": backward-kill-word'              # Insert

if _have show; then
    alias s="$NAME -p dir:-Fh -p dir:--color=auto -p dir:--group-directories-first"
    export PAGER="$NAME"
fi

if _have ag; then
    if [ -n "$PAGER" ]; then
        alias f="$NAME --follow --hidden --pager \"$PAGER\""
    else
        alias f="$NAME --follow --hidden"
    fi
fi

# https://github.com/git/git/tree/master/contrib/completion
if _have git; then
    _set_git_config() {
        local option=$1
        local value=$2

        if ! git config --global "$option" > /dev/null; then
            if [ -z "$value" ]; then
                _warn "Missing Git config: $option"
            else
                git config --global "$option" "$value"
            fi
        fi
    }

    _load_git_completions() {
        _completion_loader git
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

    for ALIAS in sa sb sc sd sh sl sp sr ss st; do
        eval "_${ALIAS}() { _load_git_completions; }"
        eval "complete -F _${ALIAS} ${ALIAS}"
    done

    if _have nano; then
        # Go to the end of the first line in commit message templates.
        export GIT_EDITOR="$NAME +,9999"
    fi

    if [ ! -e "$HOME/.config/git/ignore" ]; then
        _warn "Missing user Git ignore: ~/.config/git/ignore"
    fi

    _set_git_config push.default simple
    _set_git_config branch.autosetuprebase always
    _set_git_config user.email
    _set_git_config user.name

    export GIT_PS1_SHOWDIRTYSTATE=x
    export GIT_PS1_SHOWSTASHSTATE=x
    export GIT_PS1_SHOWUNTRACKEDFILES=x

    _color_git_ps1() {
        local ps1=$(__git_ps1 "%s")
        [ -n "$ps1" ] && echo "$ps1 "
    }

    _ps1_user_host="$_ps1_user_host\[$_green\]\$(_color_git_ps1)\[$_color_off\]"
fi

_jobs_nr_ps1() {
    local jobs=$(jobs | wc -l)
    [ $jobs -gt 0 ] && echo " $jobs"
}

if [ -z "$BASHRC_KEEP_PROMPT" ]; then
    export PS1="$_ps1_user_host\[$_b_blue\]\w\[$_color_off\]\[$_b_red\]\$(_jobs_nr_ps1)\[$_color_off\] \\$ "
fi
