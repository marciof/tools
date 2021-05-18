#!/bin/sh

# TODO document

set -e -u

pwd="$(dirname "$(readlink -e "$0")")"
ENCLOSURE_DL_BIN="${ENCLOSURE_DL_BIN:-$pwd/enclosure_download.sh}"
DL_JOB_FIND_DB_BIN="${DL_JOB_FIND_DB_BIN:-$pwd/download_jobs_find_db.sh}"
DL_JOB_CREATE_BIN="${DL_JOB_CREATE_BIN:-$pwd/download_jobs_create.sh}"
DL_JOB_DELETE_BIN="${DL_JOB_DELETE_BIN:-$pwd/download_jobs_delete.sh}"

"$ENCLOSURE_DL_BIN" \
    -a "$("$DL_JOB_FIND_DB_BIN")" \
    -b "$DL_JOB_CREATE_BIN" \
    -e "$DL_JOB_DELETE_BIN" \
    "$@"
