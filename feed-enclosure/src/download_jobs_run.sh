#!/bin/sh

# TODO document

set -e -u

# TODO check dependencies
DL_JOB_FIND_DB_BIN="${DL_JOB_FIND_DB_BIN:-$(dirname "$(readlink -e "$0")")/download_jobs_find_db.sh}"
DL_OB_DELETE_BIN="${DL_OB_DELETE_BIN:-$(dirname "$(readlink -e "$0")")/download_jobs_delete.sh}"
ENCLOSURE_DL_BIN="${ENCLOSURE_DL_BIN:-$(dirname "$(readlink -e "$0")")/enclosure_download.sh}"
RECSEL_BIN="${RECSEL_BIN:-recsel}"

jobs_db="$("$DL_JOB_FIND_DB_BIN")"
num_jobs="$("$RECSEL_BIN" -c "$jobs_db")"
job_num=0

while [ "$job_num" -lt "$num_jobs" ]; do
    job="$("$RECSEL_BIN" -n "$((num_jobs - job_num - 1))" "$jobs_db")"

    if [ -z "$job" ]; then
        break
    fi

    echo "$job"

    url="$(echo "$job" | "$RECSEL_BIN" -P URL)"
    format="$(echo "$job" | "$RECSEL_BIN" -P Format)"
    folder="$(echo "$job" | "$RECSEL_BIN" -P Folder)"

    {
        # TODO use generic download format option
        "$ENCLOSURE_DL_BIN" -y "$format" -f "$folder" -- "$url"
        "$DL_OB_DELETE_BIN" "$url" "$format" "$folder"
    }&

    # TODO option to limit number of concurrent jobs?
    job_num="$((job_num + 1))"
    # TODO option for sleep duration?
    sleep 1
done

wait
