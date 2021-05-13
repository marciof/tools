#!/bin/sh

# Lints shell scripts.
#
# Arguments: none
# Stdin: none
# Stdout: lint results
#
# Runtime dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1
#
# Test dependencies:
#   (See runtime dependencies.)

set -e -u

SHELLCHECK_BIN="${SHELLCHECK_BIN:-shellcheck}"

if ! command -v "$SHELLCHECK_BIN" >/dev/null; then
    echo "Error: $SHELLCHECK_BIN not found (override \$SHELLCHECK_BIN)" >&2
    exit 1
fi

pwd="$(dirname "$(readlink -e "$0")")"
(
    cd "$pwd"
    echo ./*.sh ../src/*.sh
    "$SHELLCHECK_BIN" -- *.sh ../src/*.sh
)
