#!/bin/sh
# https://perf.wiki.kernel.org
# apt-get install linux-tools
perf stat --sync -r 100 "${BIN:-show}" $@
