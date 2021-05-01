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
#   apt install xmlstarlet # Version: 1.6.1-2.1 # parse/modify XML
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

# TODO add a global option for auto-download and filter cmd to Liferea?

set -e -u

XML_STARLET_BIN="${XML_STARLET_BIN:-xmlstarlet}"
FEED_REBUILD_ENCLOSURES_BIN="${FEED_REBUILD_ENCLOSURES_BIN:-$(dirname "$(readlink -e "$0")")/feed_rebuild_enclosures.py}"

# Set a value for an XML attribute in an XPath location.
#
# Globals: XML_STARLET_BIN
# Arguments: XPath locator, attribute name, attribute value
# Stdin: XML
# Stdout: updated XML
xml_set_attr_value() {
    xml_locator="$1"
    xml_name="$2"
    xml_value="$3"

    "$XML_STARLET_BIN" edit -P \
        --update "$xml_locator/@$xml_name" \
        --value "$xml_value" \
        | "$XML_STARLET_BIN" edit -P \
            --insert "${xml_locator}[not(@$xml_name)]" \
            --type attr \
            -n "$xml_name" \
            --value "$xml_value"
}

if ! command -v "$XML_STARLET_BIN" >/dev/null; then
    echo "Error: $XML_STARLET_BIN not found (override \$XML_STARLET_BIN)" >&2
    exit 1
fi

if ! command -v "$FEED_REBUILD_ENCLOSURES_BIN" >/dev/null; then
    echo "Error: $FEED_REBUILD_ENCLOSURES_BIN not found (override \$FEED_REBUILD_ENCLOSURES_BIN)" >&2
    exit 1
fi

if [ -t 0 ]; then
    echo 'Warning: stdin is connected to terminal/keyboard' >&2
fi

entry_xpath='//outline[@type="rss"]'

xml_set_attr_value "$entry_xpath" encAutoDownload true \
    | xml_set_attr_value "$entry_xpath" filtercmd "$FEED_REBUILD_ENCLOSURES_BIN"
