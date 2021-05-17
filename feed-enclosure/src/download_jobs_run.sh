#!/bin/sh

# Runs all pending download jobs from the recfile database in parallel.
#
# Arguments: none
# Stdin: none
# Stdout: download jobs being run
#
# Runtime dependencies:
#   ./download_jobs_delete.sh
#   ./download_jobs_find_db.sh
#   ./enclosure_download.sh
#   apt install recutils # Version: 1.8-1
#
# Test dependencies:
#   ../tst/lint_shell.sh

set -e -u

DL_JOB_FIND_DB_BIN="${DL_JOB_FIND_DB_BIN:-$(dirname "$(readlink -e "$0")")/download_jobs_find_db.sh}"
DL_JOB_DELETE_BIN="${DL_JOB_DELETE_BIN:-$(dirname "$(readlink -e "$0")")/download_jobs_delete.sh}"
ENCLOSURE_DL_BIN="${ENCLOSURE_DL_BIN:-$(dirname "$(readlink -e "$0")")/enclosure_download.sh}"
RECSEL_BIN="${RECSEL_BIN:-recsel}"

if ! command -v "$DL_JOB_FIND_DB_BIN" >/dev/null; then
    echo "Error: $DL_JOB_FIND_DB_BIN not found (override \$DL_JOB_FIND_DB_BIN)" >&2
    exit 1
fi

if ! command -v "$DL_JOB_DELETE_BIN" >/dev/null; then
    echo "Error: $DL_JOB_DELETE_BIN not found (override \$DL_JOB_DELETE_BIN)" >&2
    exit 1
fi

if ! command -v "$ENCLOSURE_DL_BIN" >/dev/null; then
    echo "Error: $ENCLOSURE_DL_BIN not found (override \$ENCLOSURE_DL_BIN)" >&2
    exit 1
fi

if ! command -v "$RECSEL_BIN" >/dev/null; then
    echo "Error: $RECSEL_BIN not found (override \$RECSEL_BIN)" >&2
    exit 1
fi

jobs_db="$("$DL_JOB_FIND_DB_BIN")"
num_jobs="$("$RECSEL_BIN" -c "$jobs_db")"
job_num=0

while [ "$job_num" -lt "$num_jobs" ]; do
    # Most to least recent job, while also ensuring parallel jobs don't
    # interfere with each other when modifying the recfile database.
    job="$("$RECSEL_BIN" -n "$((num_jobs - job_num - 1))" "$jobs_db")"

    if [ -z "$job" ]; then
        break
    fi

    echo "$job"

    url="$(echo "$job" | "$RECSEL_BIN" -P URL)"
    format="$(echo "$job" | "$RECSEL_BIN" -P Format)"
    folder="$(echo "$job" | "$RECSEL_BIN" -P Folder)"

    {
        # TODO use the generic option for the download format
        "$ENCLOSURE_DL_BIN" -y "$format" -f "$folder" -- "$url"
        # TODO is recutils concurrency safe?
        "$DL_JOB_DELETE_BIN" "$url" "$format" "$folder"
    }&

    # TODO limit number of concurrent jobs?
    job_num="$((job_num + 1))"
    sleep 1
done

wait
