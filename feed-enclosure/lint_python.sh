#!/bin/sh

# Lints Python source code.
#
# Arguments: none
# Stdin: none
# Stdout: lint results
#
# Runtime dependencies:
#   (See requirements.txt file.)
#
# Test dependencies:
#   ./lint_shell.sh

set -e -u

MYPY_BIN="${MYPY_BIN:-mypy}"

if ! command -v "$MYPY_BIN" >/dev/null; then
    echo "Error: $MYPY_BIN not found (override \$MYPY_BIN)" >&2
    exit 1
fi

pwd="$(dirname "$(readlink -e "$0")")"
(
    cd "$pwd"
    echo ./*.py
    "$MYPY_BIN" -- *.py
)
# TODO: use PEP8 as well
