#!/bin/sh

# Lints Python source code.
#
# Arguments: none
# Stdin: none
# Stdout: lint results
#
# Runtime dependencies:
#   (See associated requirements.txt file.)
#
# Test dependencies:
#   ./lint_shell.sh

set -e -u

MYPY_BIN="${MYPY_BIN:-mypy}"
PYCODESTYLE_BIN="${PYCODESTYLE_BIN:-pycodestyle}"

if ! command -v "$MYPY_BIN" >/dev/null; then
    echo "Error: $MYPY_BIN not found (override \$MYPY_BIN)" >&2
    exit 1
fi

if ! command -v "$PYCODESTYLE_BIN" >/dev/null; then
    echo "Error: $PYCODESTYLE_BIN not found (override \$PYCODESTYLE_BIN)" >&2
    exit 1
fi

pwd="$(dirname "$(readlink -e "$0")")"
(
    cd "$pwd"
    echo ../src/*.py

    printf '\n--- Mypy ---\n'
    "$MYPY_BIN" -- ../src/*.py

    printf '\n--- pycodestyle ---\n'
    "$PYCODESTYLE_BIN" -v -- ../src/*.py
)
