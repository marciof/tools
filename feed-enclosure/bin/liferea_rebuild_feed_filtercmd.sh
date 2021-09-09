#!/bin/sh

# Wraps `feed_enclosure.feed_rewrite` for use with Liferea.

# TODO add catchall logging wrapper
# TODO honor other Python's user environment variables

set -e -u

PYTHONPATH="${PYTHONPATH:-}:$(dirname "$(readlink -e "$0")")/../"
PYTHON3="${PYTHON3:-python3}"

export PYTHONPATH
"$PYTHON3" -m feed_enclosure.feed_rewrite "$@"
