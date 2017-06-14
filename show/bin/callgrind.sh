#!/bin/sh
set -e
valgrind -q --tool=callgrind "${BIN:-show}" "$@"
kcachegrind callgrind.out.*
rm callgrind.out.*
