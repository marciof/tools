#!/bin/sh

# Transforms a Liferea's OPML file so that each feed is configured to
# automatically download enclosures.
# https://lzone.de/liferea/help110/preferences_en.html#enclosures
#
# Input: stdin in Liferea's OPML format
# Output: stdout in Liferea's OPML format
#
# Runtime dependencies:
#   apt install xmlstarlet # Version: 1.6.1-2.1
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

XML_STARLET_BIN="${XML_STARLET_BIN:-xmlstarlet}"
ENC_AUTO_DOWN_ATTR=encAutoDownload
ENC_AUTO_DOWN_XPATH="//outline[@type=\"rss\"]/@$ENC_AUTO_DOWN_ATTR"
NO_ENC_AUTO_DOWN_XPATH="//outline[@type=\"rss\"][not(@$ENC_AUTO_DOWN_ATTR)]"

if ! command -v "$XML_STARLET_BIN" >/dev/null; then
    echo "Error: $XML_STARLET_BIN not found (override \$XML_STARLET_BIN)" >&2
    exit 1
fi

if [ -t 0 ]; then
    cat <<'EOT' >&2
Warning: stdin is connected to terminal/keyboard

See companion script `liferea_find_opml.sh` for where to find
your Liferea's OPML file to feed this script with.
EOT
fi

"$XML_STARLET_BIN" edit -P --update "$ENC_AUTO_DOWN_XPATH" --value true \
    | "$XML_STARLET_BIN" edit -P --insert "$NO_ENC_AUTO_DOWN_XPATH" \
        --type attr -n "$ENC_AUTO_DOWN_ATTR" --value true
