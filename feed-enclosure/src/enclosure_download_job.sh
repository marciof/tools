#!/bin/sh

# TODO document

set -e -u

# TODO check dependencies
ENCLOSURE_DL_BIN="${ENCLOSURE_DL_BIN:-$(dirname "$(readlink -e "$0")")/enclosure_download.sh}"
DL_JOB_CREATE_BIN="${DL_JOB_CREATE_BIN:-$(dirname "$(readlink -e "$0")")/download_jobs_create.sh}"
DL_JOB_DELETE_BIN="${DL_JOB_DELETE_BIN:-$(dirname "$(readlink -e "$0")")/download_jobs_delete.sh}"

"$ENCLOSURE_DL_BIN" -b "$DL_JOB_CREATE_BIN" -e "$DL_JOB_DELETE_BIN" "$@"
