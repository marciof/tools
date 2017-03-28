#!/bin/sh

# Fix Valgrind location for tests that change `$PATH`.
export VALGRIND_PATH="`which valgrind`"

export VALGRIND_LEAK_CHECK="--leak-check=yes --show-reachable=yes"

show() {
    "$VALGRIND_PATH" -q $VALGRIND_LEAK_CHECK "$TESTDIR/../show" "$@"
}
