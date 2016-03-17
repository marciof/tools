#include <errno.h>
#include <pty.h>
#include <unistd.h>
#include "fork_exec.h"

#define NO_FD ((int) -1)

static int fork_exec_pipe(char* file, char* argv[], Error* error) {
    int stdout_read_write_fds[2];

    if (pipe(stdout_read_write_fds) == -1) {
        Error_errno(error, errno);
        return NO_FD;
    }

    int child_pid = fork();

    if (child_pid == -1) {
        Error_errno(error, errno);
        return NO_FD;
    }
    else if (child_pid != 0) {
        close(stdout_read_write_fds[1]);
        Error_clear(error);
        return stdout_read_write_fds[0];
    }

    if (dup2(stdout_read_write_fds[1], STDOUT_FILENO) == -1) {
        Error_errno(error, errno);
        return NO_FD;
    }

    close(stdout_read_write_fds[1]);
    close(stdout_read_write_fds[0]);

    execvp(file, argv);
    Error_errno(error, errno);
    return NO_FD;
}

static int fork_exec_pty(char* file, char* argv[], Error* error) {
    int saved_stderr = dup(STDERR_FILENO);

    if (saved_stderr == -1) {
        Error_errno(error, errno);
        return NO_FD;
    }

    int child_fd_out;
    int child_pid = forkpty(&child_fd_out, NULL, NULL, NULL);

    if (child_pid == -1) {
        Error_errno(error, errno);
        return NO_FD;
    }
    else if (child_pid != 0) {
        close(saved_stderr);
        Error_clear(error);
        return child_fd_out;
    }

    if (dup2(saved_stderr, STDERR_FILENO) == -1) {
        Error_errno(error, errno);
        return NO_FD;
    }

    execvp(file, argv);
    Error_errno(error, errno);
    return NO_FD;
}

int fork_exec(char* file, char* argv[], Error* error) {
    if (isatty(STDOUT_FILENO)) {
        return fork_exec_pty(file, argv, error);
    }
    else {
        return fork_exec_pipe(file, argv, error);
    }
}
