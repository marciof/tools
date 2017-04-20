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

/**
 * Wraps `popen2_status`.
 * @return `true` if it exited successfully, `false` on `ENOENT` or on error
 */
bool popen2_check(char* file, char* argv[], struct Error* error);

/** Wraps `close` and `popen2_wait`. */
void popen2_close(int fd, pid_t pid, struct Error* error);

/**
 * Wraps `read`.
 *
 * If the child process returns `EIO` instead of zero bytes on the last `read`
 * it also wraps `close` and `popen2_wait` to figure out if it was a real error,
 * and sets `pid` to `0` if it successfully exited.
 *
 * @param pid set to `0` if the process successfully exited on `EIO`
 * @return read count, or `0` on end of input or error
 * @see http://stackoverflow.com/q/43108221/753501
 */
size_t popen2_read(
    int fd, char* buffer, size_t length, pid_t* pid, struct Error* error);

/** Wraps `popen2` and `popen2_wait`. */
int popen2_status(char* file, char* argv[], struct Error* error);

/**
 * Wait for subprocesses started by `popen2`.
 *
 * @param actual_pid optional child pid returned by `waitpid`
 * @param error adds `errno` `ENOENT` if the executable doesn't exist
 * @return subprocess exit status code
 */
int popen2_wait(
    pid_t pid, pid_t* actual_pid, int waitpid_options, struct Error* error);
