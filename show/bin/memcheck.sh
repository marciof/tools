#!/bin/sh
valgrind -q --leak-check=yes --show-reachable=yes "${BIN:-show}" "$@"
