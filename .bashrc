#!/bin/bash

case "$-" in
*i*)
    INTERACTIVE=x
;;
esac

# Cygwin helper.
if [ -n "$WINDIR" -a -z "$INTERACTIVE" ]; then
    ls > /dev/null 2>&1
    
    if [ "$?" = '127' ]; then
        export CD=$@
        export HOME="/home/$USERNAME"
        exec $SHELL -il
    fi
fi

[ "$(uname -o)" = 'Cygwin' ] && export CYGWIN_ENV=x
source /etc/bash_completion 2> /dev/null

# Disable tilde expansion only.
_expand() {
    eval cur=$cur
}

_have() {
    for NAME; do
        LOCATION=$(which $NAME 2> /dev/null)
        
        if [ -n "$LOCATION" ]; then
            eval "HAVE_$(echo $NAME | tr '[:lower:]-' '[:upper:]_')='$LOCATION'"
            return 0
        fi
    done
    
    [ -n "$INTERACTIVE" ] && echo "* Missing: $@" >&2
    return 1
}

if [ -n "$INTERACTIVE" ]; then
    bind 'set completion-ignore-case On'
    bind 'set expand-tilde Off'
    bind 'set mark-symlinked-directories On'
    bind 'set visible-stats On'
    bind '"\e[1;5C": forward-word'                  # Ctrl + Right
    bind '"\e[1;5D": backward-word'                 # Ctrl + Left
    bind '"\e[3;5~": kill-word'                     # Ctrl + Delete
    bind '"\e[2;5~": backward-kill-word'            # Ctrl + Insert
    bind '"\e[2~": unix-word-rubout'                # Insert
    
    # Disable XON/XOFF flow control to allow: bind -q forward-search-history
    stty -ixon
fi

shopt -s cdspell checkwinsize histappend

alias c=cd
complete -F _cd -o nospace c

alias e='$VISUAL'
alias j=jobs
alias l='ls -CFXh --color=auto --group-directories-first'
alias ll='l -l'
alias dir='l -lA'
alias sed='sed -r'
alias -- -='c -'
alias ..='c ..'
alias ...='c ../..'
alias ....='c ../../..'
alias .....='c ../../../..'

_have ack-grep ack && alias f="$NAME --all --sort-files"
_have dircolors && eval "$($NAME -b)"
_have kwrite gedit nano && export VISUAL=$LOCATION
_have nano && export EDITOR=$LOCATION

export ACK_COLOR_FILENAME='dark blue'
export ACK_COLOR_LINENO='dark yellow'
export HARNESS_COLOR=1
export HISTCONTROL=ignoreboth
export LESS='--tabs=4 --clear-screen --LONG-PROMPT --RAW-CONTROL-CHARS'
export PYTHONDONTWRITEBYTECODE=x

# Remove bright colors.
export LS_COLORS=$(echo $LS_COLORS | sed -e 's/=01;/=30;/g')

ps1_user_host='\u@\h'

if locale -a | grep '^en_DK' -q; then
    export LC_TIME=en_DK.UTF-8                      # ISO 8601
fi

if [ -z "$CYGWIN_ENV" ]; then
    _have ksshaskpass ssh-askpass && export SSH_ASKPASS=$LOCATION
    _have lesspipe && eval "$($NAME)"
    _have setxkbmap && $NAME -option 'nbsp:none'    # Allow e.g. AltGr + Space.
    [ -z "$DISPLAY" ] && export DISPLAY=:0.0
    
    if [ "$TERM" = "xterm" ]; then
        # Save history session to file and set terminal title.
        export PROMPT_COMMAND='
            history -a
            echo -ne "\e]0;${USER}@${HOSTNAME}: ${PWD/$HOME/~}\007"'
    fi
    
    if [ "$(stat --format=%i /)" != '2' ]; then
        ps1_user_host="($ps1_user_host)"
        export CHROOT=x
        [ -n "$INTERACTIVE" ] && echo "* chroot: $(uname -srmo)"
    fi
    
    if pgrep metacity > /dev/null; then
        gconftool-2 -s -t bool \
            /apps/metacity/general/resize_with_right_button true
    fi
else
    export CYGWIN=nodosfilewarning
    export TERM=cygwin
    export TEMP=/tmp
    export TMP='$TMP'
    
    if [ -n "$INTERACTIVE" ]; then
        bind '"\e[2;2~": paste-from-clipboard'      # Shift + Insert
        [ -n "$CD" ] && cd "$(cygpath "$CD")" && unset CD
    fi
fi

_jobs_nr_ps1() {
    local jobs=$(jobs | wc -l)
    [ $jobs -gt 0 ] && echo -e ":\e[0;31m$jobs\e[00m"
}

ps1_user_host="\[\e[4;30;32m\]$ps1_user_host\[\e[00m\]\$(_jobs_nr_ps1)"

if _have cpan; then
    export FTP_PASSIVE=1
    export PERL_AUTOINSTALL=1
    export PERL_MM_USE_DEFAULT=1
    cpan_setup=~/.cpan_setup
    
    if [ ! -e "$cpan_setup" ]; then
        touch $cpan_setup
        cat << 'TEXT' | tee "$cpan_setup" | cpan
o conf init
o conf halt_on_failure 1
o conf inhibit_startup_message 1
o conf make_install_make_command "sudo make"
o conf mbuild_install_build_command "sudo ./Build"
o conf commit
TEXT
    fi
    
    unset cpan_setup
fi

if _have git; then
    alias g=$NAME
    complete -o bashdefault -o default -o nospace -F _git g
    
    _color_git_ps1() {
        local ps1=$(__git_ps1 "%s")
        [ -n "$ps1" ] && echo -e ":\e[0;33m$ps1\e[00m"
    }
    
    _set_git_config() {
        local option=$1
        local value=$2
        
        if ! git config --global "$option" > /dev/null; then
            if [ -z "$value" ]; then
                [ -n "$INTERACTIVE" ] && echo "* Missing Git config: $option" >&2
            else
                git config --global "$option" "$value"
            fi
        fi
    }
    
    _set_git_config user.email
    _set_git_config user.name
    _set_git_config color.ui auto
    _set_git_config push.default tracking
    _set_git_config alias.co checkout
    _set_git_config alias.br 'branch -vv'
    _set_git_config alias.hist 'log --graph --date=short
        --pretty=format:"%C(yellow)%h %C(green)%ad %C(reset)%s%C(yellow)%d %C(reset)(%C(blue)%aN%C(reset))"'
    _set_git_config alias.pub '!bash -c '"'"'\
        COMMAND="git push origin HEAD:refs/heads/$0 ${@:1}" \
        && echo $COMMAND \
        && $COMMAND'"'"
    _set_git_config core.editor 'bash -c "
        if pgrep kompare > /dev/null; then $EDITOR $@; else $VISUAL $@; fi"'
    
    export GIT_PS1_SHOWDIRTYSTATE=x
    export GIT_PS1_SHOWSTASHSTATE=x
    export GIT_PS1_SHOWUNTRACKEDFILES=x
    
    if [ -z "$CYGWIN_ENV" -a "$(type -t __git_ps1)" = 'function' ]; then
        ps1_user_host="$ps1_user_host\$(_color_git_ps1)"
    fi
fi

export PS1="$ps1_user_host:\[\e[01;34m\]\w\n\\$\[\e[00m\] "
unset ps1_user_host

nano_rc=~/.nanorc

if [ -n "$HAVE_NANO" -a -n "$INTERACTIVE" -a ! -e "$nano_rc" ]; then
    ls -1 /usr/share/nano/*.nanorc | sed -e 's/(.+)/include "\1"/' > "$nano_rc"
    cat << 'TEXT' >> "$nano_rc"
set autoindent
set const
set morespace
set noconvert
set nonewlines
set nowrap
set smarthome
set smooth
set suspend
set tabsize 4
set tabstospaces
TEXT
fi

unset nano_rc
kde_start_ssh_add=~/.kde/Autostart/ssh-add.sh

if [ -z "$KDE_FULL_SESSION" -o ! -e "$kde_start_ssh_add" ]; then
    ssh-add < /dev/null 2> /dev/null
    
    if  [ -n "$KDE_FULL_SESSION" ]; then
        cat << 'TEXT' > "$kde_start_ssh_add" && chmod +x "$kde_start_ssh_add"
#!/bin/sh
ssh-add
TEXT
    fi
fi

unset kde_start_ssh_add
show_py="$(dirname "$(readlink "$BASH_SOURCE")" 2> /dev/null)/show.py"

if [ -e "$show_py" ]; then
    alias s="$show_py -l-CFXh -l--color=always -l--group-directories-first"
    alias ss='s -l-l'
    alias sss='s -l-lA'
    export ACK_PAGER="$show_py -d"
    export GIT_PAGER=$show_py
else
    _have colordiff && alias diff=$NAME
fi

unset show_py

for bashrc_child in $(ls -1 "$BASH_SOURCE".* 2> /dev/null); do
    source "$bashrc_child"
    [ -n "$INTERACTIVE" ] && echo "* Loaded: $bashrc_child"
done

unset bashrc_child

_in_git() {
    git rev-parse --is-inside-work-tree > /dev/null 2>&1
}

_in_scm() {
    echo "* SCM? $(pwd)" >&2
}

_in_svn() {
    svn info > /dev/null 2>&1
}

cleanup() {
    _have apt-get && (sudo $NAME -qq autoremove; sudo $NAME -qq clean)
    perl -i -ne 'print unless $seen{$_}++' $HISTFILE
    rm -rf ~/.cpan/{build,sources}
}

ff() {
    find "$@" -a ! -name '*.svn-base'
}

reload() {
    exec $SHELL
}

sbl() {
    if _in_git; then
        git blame --date=short "$@"
    elif _in_svn; then
        svn blame "$@"
    else
        _in_scm
    fi
}

sci() {
    if _in_git; then
        local cached=$(git diff --cached --name-only | wc -l)
        
        if  [ $# -eq 0 -a $cached -eq 0 ]; then
            git commit -a
        else
            git commit "$@"
        fi
    elif _in_svn; then
        svn commit "$@"
    else
        _in_scm
    fi
}

sdi() {
    if _in_git; then
        git diff "$@"
    elif _in_svn; then
        svn diff "$@"
    else
        _in_scm
    fi
}

sl() {
    if _in_git; then
        git log "$@"
    elif _in_svn; then
        svn log "$@"
    else
        _in_scm
    fi
}

sre() {
    if _in_git; then
        git checkout "$@"
    elif _in_svn; then
        svn revert "$@"
    else
        _in_scm
    fi
}

sst() {
    if _in_git; then
        git status "$@"
    elif _in_svn; then
        svn status "$@"
    else
        _in_scm
    fi
}

sup() {
    if _in_git; then
        git pull "$@"
    elif _in_svn; then
        svn update "$@"
    else
        _in_scm
    fi
}
