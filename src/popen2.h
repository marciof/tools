#pragma once
#include <stdbool.h>
#include <sys/types.h>
#include "Error.h"

// If `is_read`, returns a file descriptor for reading the subprocess output,
// otherwise returns a file descriptor for writing to the subprocess input.
// Uses a pseudo-TTY when reading and when stdout is a TTY.
// Redirects `out_fd` and `err_fd` when either one isn't `IO_NULL_FD`.
int popen2(
    char* file,
    char* argv[],
    bool is_read,
    int out_fd,
    int err_fd,
    pid_t* pid,
    Error* error);

int popen2_status(char* file, char* argv[], Error* error);

// Use to wait for subprocesses started by `popen2`.
int wait_subprocess(pid_t child_pid, Error* error);
