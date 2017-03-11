#!/bin/sh
valgrind -q --tool=callgrind show "$@"
kcachegrind callgrind.out.*
rm callgrind.out.*
