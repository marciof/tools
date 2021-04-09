#!/bin/sh

# Modifies a Liferea's OPML file so that each feed is configured to
# automatically download enclosures.
#
# See Liferea's documentation:
# https://lzone.de/liferea/help110/preferences_en.html#enclosures
#
# Runtime dependencies:
#   apt install xmlstarlet # Version: 1.6.1-2.1
#
# Test dependencies:
#   apt install shellcheck # Version: 0.7.1-1build1

set -e -u

print_usage() {
    cat <<EOT >&2
Input: stdin Liferea OPML file
Output: stdout Liferea OPML file

See <https://lzone.de/liferea/faq.htm#how-to-copy-remote> for where to find
your Liferea's OPML file.
EOT
}

XML_STARLET_BIN="${XML_STARLET_BIN:-xmlstarlet}"

if ! command -v "$XML_STARLET_BIN" >/dev/null; then
    echo "Error: command $XML_STARLET_BIN not found (override \$XML_STARLET_BIN)" >&2
    exit 1
fi

# TODO: add option to use the default OPML file?
if [ -t 0 ]; then
    echo 'Warning: stdin is connected to terminal/keyboard' >&2
    echo >&2
    print_usage
fi

"$XML_STARLET_BIN" edit -P --update '//outline[@type="rss"]/@encAutoDownload' --value true \
    | "$XML_STARLET_BIN" edit -P --insert '//outline[@type="rss"][not(@encAutoDownload)]' --type attr -n encAutoDownload --value true
