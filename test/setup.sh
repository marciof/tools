#!/bin/sh
alias show="valgrind -q --leak-check=yes --show-leak-kinds=all $TESTDIR/../show"
