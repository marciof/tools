#!/bin/bash

if [[ "$-" =~ 'i' ]]; then
    _warn() {
        echo "* $@" >&2
    }
else
    _warn() {
        :
    }
fi

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

alias j=jobs
alias -- -='cd -'
alias ..='cd ..'

if ls --group-directories-first 2> /dev/null; then
    _ls_group_dir_opt=--group-directories-first
else
    _ls_group_dir_opt=
fi

alias l="ls -CFXh --color=auto $_ls_group_dir_opt"
alias ll='l -lA'

_have dircolors && eval "$($NAME -b)"
_have ksshaskpass ssh-askpass && export SSH_ASKPASS=$LOCATION
_have lesspipe && eval "$($NAME)"

export HISTCONTROL=ignoreboth
export LESS='--tabs=4 --clear-screen --LONG-PROMPT --RAW-CONTROL-CHARS'
export PYTHONDONTWRITEBYTECODE=x
export VIRTUAL_ENV_DISABLE_PROMPT=x

# Remove bright colors (must come after `dircolors`).
export LS_COLORS=$(echo $LS_COLORS | sed -e 's/=01;/=30;/g')

# https://wiki.archlinux.org/index.php/Color_Bash_Prompt
_color_off='\e[0m'
_yellow='\e[0;33m'
_purple='\e[0;35m'
_b_red='\e[1;31m'
_b_blue='\e[1;34m'
_u_green='\e[4;32m'

_ps1_user_host='\u@\h'
_show_py="$(dirname "$(readlink "$BASH_SOURCE")" 2> /dev/null)/show.py"
_ssh_add_auto_start="$HOME/.kde/Autostart/ssh-add.sh"

if [[ "$-" =~ 'i' ]]; then
    # Disable XON/XOFF flow control to allow: bind -q forward-search-history
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
fi

if [ -e "$_show_py" ]; then
    if [ -n "$_ls_group_dir_opt" ]; then
        _ls_group_dir_opt="-l$_ls_group_dir_opt"
    fi

    alias s="\"$_show_py\" -l-CFXh -l--color=always $_ls_group_dir_opt"
    alias ss='s -l-lA'
    export GIT_PAGER=$_show_py
fi

if _have ag; then
    if [ -e "$_show_py" ]; then
        _ag_pager="--pager 'python $_show_py -d'"
    else
        _ag_pager=''
    fi

    alias f="$NAME $_ag_pager --color-path '0;34' --color-line-number '0;33' --follow --hidden"
fi

if [ -n "$KDE_FULL_SESSION" -a ! -e "$_ssh_add_auto_start" ]; then
    cat << 'SCRIPT' > "$_ssh_add_auto_start"
#!/bin/sh
ssh-add < /dev/null 2> /dev/null
SCRIPT
    chmod +x "$_ssh_add_auto_start"
fi

# Dates in ISO 8601 format.
if locale -a 2> /dev/null | grep -q '^en_DK'; then
    export LC_TIME=en_DK.UTF-8
else
    _warn 'Select "en_DK.UTF-8": $ dpkg-reconfigure locales'
fi

# Allow AltGr + Space to be interpreted as a regular blank space.
if _have setxkbmap && ! $NAME -option 'nbsp:none' 2> /dev/null; then
    _warn 'Install XKB data: $ apt-get install xkb-data'
fi

_jobs_nr_ps1() {
    local jobs=$(jobs | wc -l)
    [ $jobs -gt 0 ] && echo -e ":$_b_red$jobs$_color_off"
}

_ps1_user_host="\[$_u_green\]$_ps1_user_host\[$_color_off\]\$(_jobs_nr_ps1)"

if _have git; then
    alias g=$NAME

    if ! type -t _git > /dev/null; then
        _completion_loader git
    fi

    alias sb='git blame --date=short "$@"'
    alias sd='git diff "$@"'
    alias sl='git log --graph --pretty="format:%C(yellow)%h%C(reset) -- %s %C(green)%ai %C(cyan)%aN%C(blue)%d" "$@"'
    alias sr='git checkout "$@"'
    alias st='git status "$@"'
    alias sp='git pull "$@"'

    sc() {
        local cached=$(git diff --cached --name-only | wc -l)

        if  [ $# -eq 0 -a $cached -eq 0 ]; then
            git commit -a
        else
            git commit "$@"
        fi
    }

    complete -o bashdefault -o default -o nospace -F _git g

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
    _set_git_config color.ui auto
    _set_git_config core.whitespace -trailing-space
    _set_git_config push.default tracking
    _set_git_config user.email
    _set_git_config user.name

    if _have nano; then
        # Go to the end of the first line in commit message templates.
        export GIT_EDITOR="$NAME +,9999"
    fi;

    export GIT_PS1_SHOWDIRTYSTATE=x
    export GIT_PS1_SHOWSTASHSTATE=x
    export GIT_PS1_SHOWUNTRACKEDFILES=x

    _ps1_user_host="$_ps1_user_host\$(_color_git_ps1)"
fi

_virtual_env_ps1() {
    [ -n "$VIRTUAL_ENV" ] && echo -e ":$_purple$(basename $VIRTUAL_ENV)$_color_off"
}

for bashrc_child in $(ls -1 "$BASH_SOURCE".* 2> /dev/null); do
    source "$bashrc_child"
    _warn "Loaded: $bashrc_child"
done

export PS1="$_ps1_user_host\$(_virtual_env_ps1):\[$_b_blue\]\w\n\\$\[$_color_off\] "
