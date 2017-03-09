#!/bin/sh
valgrind -q --leak-check=yes --show-reachable=yes show $@
