#!/bin/sh

# TODO document

set -e -u

pwd="$(dirname "$(readlink -e "$0")")"
ENCLOSURE_DL_BIN="${ENCLOSURE_DL_BIN:-$pwd/enclosure_download.sh}"
DL_JOB_CREATE_BIN="${DL_JOB_CREATE_BIN:-$pwd/download_jobs_create.sh}"
DL_JOB_DELETE_BIN="${DL_JOB_DELETE_BIN:-$pwd/download_jobs_delete.sh}"

# TODO ideally, job create/delete would be decoupled from finding the DB
"$ENCLOSURE_DL_BIN" -b "$DL_JOB_CREATE_BIN" -e "$DL_JOB_DELETE_BIN" "$@"
