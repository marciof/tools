#!/bin/sh

# Sets an XML attribute value at an XPath location.
#
# Arguments: locator name value
# Stdin: XML
# Stdout: updated XML
#
# Runtime dependencies:
#   apt install xmlstarlet # Version: 1.6.1-2.1
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

XML_STARLET_BIN="${XML_STARLET_BIN:-xmlstarlet}"

if ! command -v "$XML_STARLET_BIN" >/dev/null; then
    echo "Error: $XML_STARLET_BIN not found (override \$XML_STARLET_BIN)" >&2
    exit 1
fi

if [ $# -ne 3 ]; then
    echo 'Usage: locator name value <stdin >stdout' >&2
    exit 1
fi

if [ -t 0 ]; then
    echo 'Warning: stdin is connected to terminal/keyboard' >&2
fi

locator="$1"
name="$2"
value="$3"
shift 3

with_attr_xpath="$locator/@$name"
without_attr_xpath="${locator}[not(@$name)]"

"$XML_STARLET_BIN" edit -P --update "$with_attr_xpath" --value "$value" \
    | "$XML_STARLET_BIN" edit -P --insert "$without_attr_xpath" \
        --type attr -n "$name" --value "$value"
