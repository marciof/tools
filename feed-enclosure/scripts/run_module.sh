#!/bin/sh

# Runs a Python module (useful for Liferea).
#
# Arguments: module arguments...

# TODO add catchall logging wrapper
# TODO honor other Python's user environment variables

set -e -u

module_name="$1"
shift

PYTHONPATH="${PYTHONPATH:-}:$(dirname "$(readlink -e "$0")")/../"
PYTHON3="${PYTHON3:-python3}"

export PYTHONPATH
"$PYTHON3" -m "feed_enclosure.$module_name" "$@"
