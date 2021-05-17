#!/bin/sh

# Lints Python source code.
#
# Arguments: none
# Stdin: none
# Stdout: lint results
#
# Dependencies:
#   (See associated requirements.txt file.)

set -e -u

MYPY_BIN="${MYPY_BIN:-mypy}"
PYCODESTYLE_BIN="${PYCODESTYLE_BIN:-pycodestyle}"
pwd="$(dirname "$(readlink -e "$0")")"

(
    cd "$pwd"
    echo ../src/*.py

    printf '\n--- Mypy ---\n'
    "$MYPY_BIN" -- ../src/*.py

    printf '\n--- pycodestyle ---\n'
    "$PYCODESTYLE_BIN" -v -- ../src/*.py
)
