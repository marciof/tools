#pragma once
#include <stdbool.h>
#include <sys/types.h>
#include "Error.h"

/**
 * Uses a pseudo-TTY when `is_read` is `true` and `stdout` is a TTY.
 *
 * @param is_read `true`/`false` to read/write the subprocess output/input
 * @param out_fd where to redirect `stdout` to unless `IO_NULL_FD`
 * @param err_fd where to redirect `stderr` to unless `IO_NULL_FD`
 * @return file descriptor for reading/writing the subprocess output/input
 */
int popen2(
    char* file,
    char* argv[],
    bool is_read,
    int out_fd,
    int err_fd,
    pid_t* pid,
    struct Error* error);

int popen2_status(char* file, char* argv[], struct Error* error);

/**
 * Wait for subprocesses started by `popen2`.
 *
 * @param error adds `errno` `ENOENT` if the executable doesn't exist
 * @return subprocess exit status code
 */
int popen2_wait(pid_t child_pid, struct Error* error);
