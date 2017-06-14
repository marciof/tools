#!/bin/sh
# https://perf.wiki.kernel.org
# apt install linux-tools
perf stat --sync -r 100 "${BIN:-show}" "$@"
