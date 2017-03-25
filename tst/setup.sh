#!/bin/sh
set -e -u
export SHOW_PTY="$(command -v valgrind) -q --leak-check=yes --show-reachable=yes pty"
alias show.sh='$TESTDIR/../src/show.sh'
