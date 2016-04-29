#!/bin/bash

if [[ ! "$-" =~ 'i' ]]; then
    if [[ $_ != $0 ]]; then
        return 0
    else
        exit 0
    fi
fi

_warn() {
    echo "* $@" >&2
}

for bashrc_child in $(ls -1 "$BASH_SOURCE".* 2> /dev/null); do
    source "$bashrc_child"
    _warn "Loaded: $bashrc_child"
done

if [ -e /etc/bash_completion ]; then
    source /etc/bash_completion
else
    _warn 'Missing: bash-completion'
fi

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

shopt -s cdspell checkwinsize histappend

alias -- -='cd -'
alias ..='cd ..'
alias ...='cd ../..'

_have dircolors && eval "$($NAME -b)"
_have ksshaskpass ssh-askpass && export SSH_ASKPASS=$LOCATION
_have lesspipe && eval "$($NAME)"

export ANSIBLE_NOCOWS=x
export HISTCONTROL=ignoreboth
export LESS='-x4 -c -M -R -i'
export PYTHONDONTWRITEBYTECODE=x
export VIRTUAL_ENV_DISABLE_PROMPT=x

# https://wiki.archlinux.org/index.php/Color_Bash_Prompt
_color_off='\e[0m'
_yellow='\e[0;33m'
_purple='\e[0;35m'
_b_red='\e[1;31m'
_b_blue='\e[1;34m'
_u_green='\e[4;32m'

_ps1_user_host='\u@\h'

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
    alias s="$NAME -p ls:-Fh -p ls:--color=auto -p ls:--group-directories-first"
fi

if _have ag; then
    alias f="$NAME --follow --hidden"
fi

# https://wiki.archlinux.org/index.php/KDE_Wallet#Using_the_KDE_Wallet_to_store_ssh_keys
if [ -n "$KDE_FULL_SESSION" ]; then
    if [ -d "$HOME/.kde/Autostart" ]; then
        _ssh_add_auto_start="$HOME/.kde/Autostart/ssh-add.sh"
    else
        _ssh_add_auto_start="$HOME/.config/autostart-scripts/ssh-add.sh"
    fi

    if [ ! -e "$_ssh_add_auto_start" ]; then
        cat << 'SCRIPT' > "$_ssh_add_auto_start"
#!/bin/sh
ssh-add < /dev/null 2> /dev/null
SCRIPT
        chmod +x "$_ssh_add_auto_start"
    fi
fi

_jobs_nr_ps1() {
    local jobs=$(jobs | wc -l)
    [ $jobs -gt 0 ] && echo -e ":$_b_red$jobs$_color_off"
}

_ps1_user_host="\[$_u_green\]$_ps1_user_host\[$_color_off\]\$(_jobs_nr_ps1)"

# https://github.com/git/git/tree/master/contrib/completion
if _have git; then
    alias g=$NAME

    alias sb='g blame --date=short "$@"'
    alias sl='g log --graph --pretty="tformat:%C(yellow)%h%C(reset) -- %s %C(green)%ai %C(cyan)%aN%C(blue)%d" "$@"'
    alias sp='g push "$@"'
    alias sr='g checkout "$@"'
    alias ss='g pull "$@"'
    alias st='g status "$@"'

    if _have kompare; then
        alias sd='GIT_PAGER="kompare -o -" g diff --no-color "$@"'
    else
        alias sd='g diff "$@"'
    fi

    sc() {
        local cached=$(git diff --cached --name-only | wc -l)

        if  [ $# -eq 0 -a $cached -eq 0 ]; then
            git commit -a
        else
            git commit "$@"
        fi
    }

    if type -t _completion_loader > /dev/null; then
        _completion_loader git
    fi

    complete -o bashdefault -o default -o nospace -F _git g

    __git_complete sc _git_commit
    __git_complete sd _git_diff
    __git_complete sl _git_log
    __git_complete sp _git_push
    __git_complete sr _git_checkout
    __git_complete ss _git_pull

    _color_git_ps1() {
        local ps1=$(__git_ps1 "%s")
        [ -n "$ps1" ] && echo -e ":$_yellow$ps1$_color_off"
    }

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

    _set_git_config alias.br 'branch -vv'
    _set_git_config alias.co checkout
    _set_git_config alias.re rebase
    _set_git_config color.ui auto
    _set_git_config core.whitespace -trailing-space
    _set_git_config push.default tracking
    _set_git_config branch.autosetuprebase always
    _set_git_config user.email
    _set_git_config user.name

    if _have nano; then
        # Go to the end of the first line in commit message templates.
        export GIT_EDITOR="$NAME +,9999"

        if ! grep -qsF 'set nowrap' ~/.nanorc; then
            echo 'set nowrap' >> ~/.nanorc
        fi
    fi

    export GIT_PS1_SHOWDIRTYSTATE=x
    export GIT_PS1_SHOWSTASHSTATE=x
    export GIT_PS1_SHOWUNTRACKEDFILES=x

    _ps1_user_host="$_ps1_user_host\$(_color_git_ps1)"
fi

_virtual_env_ps1() {
    [ -n "$VIRTUAL_ENV" ] && echo -e ":$_purple$(basename $VIRTUAL_ENV)$_color_off"
}

export PS1="$_ps1_user_host\$(_virtual_env_ps1):\[$_b_blue\]\w\[$_color_off\]\n\\$ "
