#!/bin/sh

# Runs all pending download jobs from a recfile database.
# Jobs are run in parallel.
#
# Dependencies:
#   ./download_jobs_delete.sh
#   ./enclosure_download.sh
#   apt install recutils # Version: 1.8-1

set -e -u

pwd="$(dirname "$(readlink -e "$0")")"
DL_JOB_DELETE_BIN="${DL_JOB_DELETE_BIN:-$pwd/download_jobs_delete.sh}"
ENCLOSURE_DL_BIN="${ENCLOSURE_DL_BIN:-$pwd/enclosure_download.sh}"
RECSEL_BIN="${RECSEL_BIN:-recsel}"

if [ $# -ne 1 ]; then
    echo 'Usage: database' >&2
    exit 1
fi

database="$1"
shift

num_jobs="$("$RECSEL_BIN" -c "$database")"
job_num=0

while [ "$job_num" -lt "$num_jobs" ]; do
    # Most to least recent job, while also ensuring parallel jobs don't
    # interfere with each other when modifying the recfile database.
    job="$("$RECSEL_BIN" -n "$((num_jobs - job_num - 1))" "$database")"

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
        # TODO is a recutils database concurrent?
        "$DL_JOB_DELETE_BIN" "$url" "$format" "$folder"
    }&

    # TODO limit number of concurrent jobs?
    job_num="$((job_num + 1))"
done

wait
