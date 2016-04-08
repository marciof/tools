#!/bin/sh
alias show="valgrind -q --leak-check=yes --show-reachable=yes $TESTDIR/../show -x pager"
