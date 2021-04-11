#!/bin/sh

# Transforms a Liferea's OPML file so that each feed is configured to
# automatically download enclosures.
# https://lzone.de/liferea/help110/preferences_en.html#enclosures
#
# Arguments: none
# Stdin: Liferea's OPML format
# Stdout: updated Liferea's OPML format
#
# Runtime dependencies:
#   ./xml_set_attr_value.sh
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

XML_SET_ATTR_VALUE_BIN="${XML_SET_ATTR_VALUE_BIN:-$(dirname "$0")/xml_set_attr_value.sh}"
FEED_REBUILD_ENCLOSURES_BIN="${FEED_REBUILD_ENCLOSURES_BIN:-$(dirname "$(readlink -e "$0")")/feed_rebuild_enclosures.py}"
entry_xpath='//outline[@type="rss"]'

if [ -t 0 ]; then
    cat <<'EOT' >&2
Warning: stdin is connected to terminal/keyboard

See companion script `liferea_find_opml.sh` for where to find
your Liferea's OPML file to feed this script with.
EOT
fi

"$XML_SET_ATTR_VALUE_BIN" "$entry_xpath" encAutoDownload true \
    | "$XML_SET_ATTR_VALUE_BIN" "$entry_xpath" filtercmd "$FEED_REBUILD_ENCLOSURES_BIN"
