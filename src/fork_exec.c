#include <errno.h>
#include <pty.h>
#include <unistd.h>
#include "fork_exec.h"
#include "io.h"

static int fork_exec_pipe(char* file, char* argv[], int* pid, Error* error) {
    int read_write_fds[2];

    if (pipe(read_write_fds) == -1) {
        ERROR_ERRNO(error, errno);
        return IO_INVALID_FD;
    }

    int child_pid = fork();

    if (child_pid == -1) {
        ERROR_ERRNO(error, errno);
        return IO_INVALID_FD;
    }
    else if (child_pid) {
        *pid = child_pid;
        close(read_write_fds[1]);
        ERROR_CLEAR(error);
        return read_write_fds[0];
    }

    if (dup2(read_write_fds[1], STDOUT_FILENO) == -1) {
        ERROR_ERRNO(error, errno);
        return IO_INVALID_FD;
    }

    close(read_write_fds[0]);
    close(read_write_fds[1]);

    execvp(file, argv);
    ERROR_ERRNO(error, errno);
    return IO_INVALID_FD;
}

static int fork_exec_pty(char* file, char* argv[], int* pid, Error* error) {
    int child_fd_out;
    int child_pid = forkpty(&child_fd_out, NULL, NULL, NULL);

    if (child_pid == -1) {
        ERROR_ERRNO(error, errno);
        return IO_INVALID_FD;
    }
    else if (child_pid) {
        *pid = child_pid;
        ERROR_CLEAR(error);
        return child_fd_out;
    }

    execvp(file, argv);
    ERROR_ERRNO(error, errno);
    return IO_INVALID_FD;
}

int fork_exec(char* file, char* argv[], int* pid, Error* error) {
    if (isatty(STDOUT_FILENO)) {
        return fork_exec_pty(file, argv, pid, error);
    }
    else {
        return fork_exec_pipe(file, argv, pid, error);
    }
}
