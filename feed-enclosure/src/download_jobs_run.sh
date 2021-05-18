#!/bin/sh

# Runs all pending download jobs from the recfile database in parallel.
#
# Arguments: none
# Stdin: none
# Stdout: download jobs being run
#
# Dependencies:
#   ./download_jobs_delete.sh
#   ./download_jobs_find_db.sh
#   ./enclosure_download.sh
#   apt install recutils # Version: 1.8-1

set -e -u

pwd="$(dirname "$(readlink -e "$0")")"
DL_JOB_DELETE_BIN="${DL_JOB_DELETE_BIN:-$pwd/download_jobs_delete.sh}"
DL_JOB_FIND_DB_BIN="${DL_JOB_FIND_DB_BIN:-$pwd/download_jobs_find_db.sh}"
ENCLOSURE_DL_BIN="${ENCLOSURE_DL_BIN:-$pwd/enclosure_download.sh}"
RECSEL_BIN="${RECSEL_BIN:-recsel}"

# TODO ideally, this would be decoupled from finding the DB
jobs_db="$("$DL_JOB_FIND_DB_BIN")"
num_jobs="$("$RECSEL_BIN" -c "$jobs_db")"
job_num=0

# TODO run from a Liferea plugin on feed updates?
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
