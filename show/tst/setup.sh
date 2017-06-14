#!/bin/sh
set -u
valgrind_path="$(command -v valgrind)"
show_path="$(command -v show)"
alias show="${valgrind_path:?} -q --leak-check=yes --show-reachable=yes ${show_path:?}"
