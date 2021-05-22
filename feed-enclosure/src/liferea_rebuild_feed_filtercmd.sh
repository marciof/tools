#!/bin/sh

# Wraps `feed_enclosure.feed_rebuilder` for use with Liferea.

# TODO add catchall logging wrapper?

set -e -u

PYTHONPATH="${PYTHONPATH:-}:$(dirname "$(readlink -e "$0")")"
PYTHON3="${PYTHON3:-python3}"

export PYTHONPATH
"$PYTHON3" -m feed_enclosure.feed_rebuilder "$@"
