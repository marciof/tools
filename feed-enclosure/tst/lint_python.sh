#!/bin/sh

# Lints Python source code.
#
# Stdout: lint results
#
# Dependencies:
#   (See associated requirements.txt file.)

set -e -u

MYPY_BIN="${MYPY_BIN:-mypy}"
PYCODESTYLE_BIN="${PYCODESTYLE_BIN:-pycodestyle}"
pwd="$(dirname "$(readlink -e "$0")")"

printf '%s\n' '--- Mypy ---'
"$MYPY_BIN" -- "$pwd/../src/"

printf '\n--- pycodestyle ---\n'
"$PYCODESTYLE_BIN" --exclude=.mypy_cache -- "$pwd/../src/"
