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

_warn() {
    [ -n "$INTERACTIVE" ] && echo "* $@" >&2
}

[ "$(uname -o)" = 'Cygwin' ] && export CYGWIN_ENV=x

if [ -z "$CYGWIN_ENV" ]; then
    if [ -e /etc/bash_completion ]; then
        source /etc/bash_completion
        complete -F _cd -o nospace c
    else
        _warn 'Missing: bash-completion'
    fi
fi

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
    
    _warn "Missing: $@"
    return 1
}

_add_to_auto_start() {
    local script="$HOME/.kde/Autostart/$1"
    
    if [ -z "$KDE_FULL_SESSION" -o ! -e "$script" ]; then
        local temp_script="$(mktemp)"
        
        chmod +x "$temp_script"
        cat > "$temp_script"
        "$temp_script" || return 1
        
        if  [ -n "$KDE_FULL_SESSION" ]; then
            mv "$temp_script" "$script"
        fi
    fi
    
    return 0
}

if [ -n "$INTERACTIVE" ]; then
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

shopt -s cdspell checkwinsize histappend

alias c=cd
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

_have nano && export EDITOR=$LOCATION

export ACK_COLOR_FILENAME='dark blue'
export ACK_COLOR_LINENO='dark yellow'
export BUSTER_TEST_OPT='-C dim'
export HARNESS_COLOR=1
export HISTCONTROL=ignoreboth
export LESS='--tabs=4 --clear-screen --LONG-PROMPT --RAW-CONTROL-CHARS'
export PATH="$PATH:node_modules/.bin"
export PYTHONDONTWRITEBYTECODE=x
export VIRTUAL_ENV_DISABLE_PROMPT=x

# https://wiki.archlinux.org/index.php/Color_Bash_Prompt
Color_Off='\e[0m'
Yellow='\e[0;33m'
Purple='\e[0;35m'
BRed='\e[1;31m'
BBlue='\e[1;34m'
UGreen='\e[4;32m'

ps1_user_host='\u@\h'

if [ -z "$CYGWIN_ENV" ]; then
    _have ack-grep ack && alias f="$NAME --all --sort-files"
    _have dircolors && eval "$($NAME -b)"
    _have kwrite gedit nano && export VISUAL=$LOCATION
    _have ksshaskpass ssh-askpass && export SSH_ASKPASS=$LOCATION
    _have lesspipe && eval "$($NAME)"

    # Remove bright colors (has to come after `dircolors`).
    export LS_COLORS=$(echo $LS_COLORS | sed -e 's/=01;/=30;/g')

    [ -z "$DISPLAY" ] && export DISPLAY=:0.0
    
    [ -z "$JAVA_HOME" ] && _have javac && \
        export JAVA_HOME=$(dirname $(dirname $(readlink -e $(which javac))))
    
    [ -z "$JRE_HOME" ] && _have java && \
        export JRE_HOME=$(dirname $(dirname $(readlink -e $(which java))))
    
    _add_to_auto_start 'ssh-add.sh' << 'SCRIPT'
#!/bin/sh
ssh-add < /dev/null 2> /dev/null
SCRIPT
    
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
    
    if _have mysql && grep -q -s '(STRICT_TRANS_TABLES|ANSI_QUOTES)' /etc/mysql/conf.d/*; then
        _warn 'Non-strict MySQL: $ $EDITOR /etc/mysql/conf.d/strict-mode.cnf'
        _warn '    [mysqld]'
        _warn '    sql-mode=STRICT_TRANS_TABLES,ANSI_QUOTES'
    fi
    
    if [ "$TERM" = "xterm" ]; then
        # Save history session to file and set terminal title.
        export PROMPT_COMMAND='
            history -a
            echo -ne "\e]0;${USER}@${HOSTNAME}: ${PWD/$HOME/~}\007"'
    fi
    
    if [ "$(stat --format=%i /)" != '2' ]; then
        ps1_user_host="($ps1_user_host)"
        export CHROOT=x
        _warn "chroot: $(uname -srmo)"
    fi
    
    if pgrep metacity > /dev/null; then
        _have gconftool-2 && $NAME -s -t bool \
            /apps/metacity/general/resize_with_right_button true
    fi
    
    show_py="$(dirname "$(readlink "$BASH_SOURCE")" 2> /dev/null)/show.py"
    
    if [ -e "$show_py" ]; then
        alias s="\"$show_py\" -l-CFXh -l--color=always -l--group-directories-first"
        alias ss='s -l-l'
        alias sss='ss -l-A'
        export ACK_PAGER="\"$show_py\" -d"
        export GIT_PAGER=$show_py
    else
        _have colordiff && alias diff=$NAME
    fi

    unset show_py
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

ps1_user_host="\[$UGreen\]$ps1_user_host\[$Color_Off\]"

if [ -z "$CYGWIN_ENV" ]; then
    _jobs_nr_ps1() {
        local jobs=$(jobs | wc -l)
        [ $jobs -gt 0 ] && echo -e ":$BRed$jobs$Color_Off"
    }
    
    ps1_user_host="$ps1_user_host\$(_jobs_nr_ps1)"
fi

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
        
        if [ -n "$ps1" ]; then
            echo -e ":$Yellow$(echo "$ps1" | sed 's/^master( |$)/./')$Color_Off"
        fi
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
    
    if [ -z "$CYGWIN_ENV" ]; then
        new_line_commit_template='~/.git-commit-template'
        echo > "$(eval echo "$new_line_commit_template")"
        
        _set_git_config alias.br 'branch -vv'
        _set_git_config alias.co checkout
        _set_git_config color.ui auto
        _set_git_config commit.template "$new_line_commit_template"
        _set_git_config core.whitespace -trailing-space
        _set_git_config user.email
        _set_git_config user.name
    fi
    
    _set_git_config push.default tracking
    
    _set_git_config alias.pub '!bash -c '"'"'\
        COMMAND="git push origin HEAD:refs/heads/$0 ${@:1}" \
        && echo $COMMAND \
        && $COMMAND'"'"
    
    export GIT_EDITOR="$EDITOR"
    export GIT_PS1_SHOWDIRTYSTATE=x
    export GIT_PS1_SHOWSTASHSTATE=x
    export GIT_PS1_SHOWUNTRACKEDFILES=x
    
    if [ -z "$CYGWIN_ENV" -a "$(type -t __git_ps1)" = 'function' ]; then
        ps1_user_host="$ps1_user_host\$(_color_git_ps1)"
    fi
fi

if [ -z "$CYGWIN_ENV" ]; then
    _virtual_env_ps1() {
        [ -n "$VIRTUAL_ENV" ] && echo -e ":$Purple$(basename $VIRTUAL_ENV)$Color_Off"
    }
    
    ps1_user_host="$ps1_user_host\$(_virtual_env_ps1)"
fi

export PS1="$ps1_user_host:\[$BBlue\]\w\n\\$\[$Color_Off\] "
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

_in_git() {
    git rev-parse --is-inside-work-tree > /dev/null 2>&1
}

_in_scm() {
    echo "* SCM? $(pwd)" >&2
}

_in_svn() {
    svn info > /dev/null 2>&1
}

mkchroot() {
    local dist=squeeze
    local chroot_dir="/var/chroot/$dist"
    local debian_sys_url=http://ftp.debian.org/debian/

    local sudoers_file=/etc/sudoers
    local no_pwd_entry="$(whoami) ALL=NOPASSWD: $(which chroot)"

    local fs_file=/etc/fstab
    local home_mount="/home $chroot_dir/home none bind,auto 0 0"
    local tmp_mount="/tmp $chroot_dir/tmp none bind,auto 0 0"
    local devpts_mount="devpts $chroot_dir/dev/pts devpts defaults 0 0"
    local proc_mount="proc $chroot_dir/proc proc defaults 0 0"

    if ! sudo fgrep -q "$no_pwd_entry" "$sudoers_file"; then
        echo '* Adding sudoers entry for password-less chroot.'
        sudo su -c "echo -e '\n$no_pwd_entry' >> '$sudoers_file'"
    fi

    sudo apt-get install -y debootstrap
    sudo mkdir -p -v "$chroot_dir"

    if [ ! -d "$chroot_dir/debootstrap" ]; then
        sudo debootstrap --keep-debootstrap-dir \
            "$dist" "$chroot_dir" "$debian_sys_url"
    fi

    for mount in "$home_mount" "$tmp_mount" "$devpts_mount" "$proc_mount"; do
        if ! fgrep -q "$mount" "$fs_file"; then
            echo "* Adding fstab entry for mount point: $mount"
            sudo su -c "echo -e '\n$mount' >> '$fs_file'"
        fi
    done

    sudo mount -a -v
    sudo cp -b -v {,$chroot_dir}/etc/resolv.conf

    for path in /etc/{passwd,shadow,group,gshadow,sudoers,hosts}; do
        sudo ln -b -v "$(readlink -e "$path")" "$chroot_dir/$path"
    done

    sudo chroot "$chroot_dir" "$SHELL" -c \
        'apt-get update; apt-get install -y --force-yes sudo locales'
    
    echo "* Ready: $ sudo chroot '$chroot_dir' \$SHELL -c \"su \$(whoami)\""
    return 0
}

cleanup() {
    _have apt-get && (sudo $NAME -qq autoremove; sudo $NAME -qq clean)
    perl -i -ne 'print unless $seen{$_}++' $HISTFILE
    rm -rf ~/.cpan/{build,sources}
}

ff() {
    find "$@" -a ! -name '*.svn-base'
}

iwait() {
    for PID in "$@"; do
        while kill -0 "$PID" 2> /dev/null; do
            sleep 0.5
        done
    done
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

if [ -z "$CYGWIN_ENV" ]; then
    for bashrc_child in $(ls -1 "$BASH_SOURCE".* 2> /dev/null); do
        source "$bashrc_child"
        _warn "Loaded: $bashrc_child"
    done
    
    unset bashrc_child
fi
