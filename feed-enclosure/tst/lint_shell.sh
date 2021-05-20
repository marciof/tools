#!/bin/sh

# Lints shell scripts.
#
# Stdout: lint results
#
# Dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

SHELLCHECK_BIN="${SHELLCHECK_BIN:-shellcheck}"
pwd="$(dirname "$(readlink -e "$0")")"

find "$pwd/.." -iname '*.sh' -exec "$SHELLCHECK_BIN" {} +
