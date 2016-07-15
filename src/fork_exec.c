#include <errno.h>
#include <fcntl.h>
#include <pty.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>
#include "fork_exec.h"
#include "io.h"

static int fork_exec_pipe(char* file, char* argv[], int* pid, Error* error) {
    int read_write_fds[2];

    if (pipe(read_write_fds) == -1) {
        Error_add(error, strerror(errno));
        return IO_INVALID_FD;
    }

    int child_pid = fork();

    if (child_pid == -1) {
        Error_add(error, strerror(errno));
        return IO_INVALID_FD;
    }
    else if (child_pid) {
        *pid = child_pid;
        close(read_write_fds[1]);
        return read_write_fds[0];
    }

    // FIXME: cleanup fork
    if (dup2(read_write_fds[1], STDOUT_FILENO) == -1) {
        Error_add(error, strerror(errno));
        return IO_INVALID_FD;
    }

    close(read_write_fds[0]);
    close(read_write_fds[1]);
    execvp(file, argv);

    // FIXME: cleanup fork
    Error_add(error, strerror(errno));
    return IO_INVALID_FD;
}

static int fork_exec_pty(char* file, char* argv[], int* pid, Error* error) {
    int child_fd_out;
    int child_pid = forkpty(&child_fd_out, NULL, NULL, NULL);

    if (child_pid == -1) {
        Error_add(error, strerror(errno));
        return IO_INVALID_FD;
    }
    else if (child_pid) {
        *pid = child_pid;
        return child_fd_out;
    }

    execvp(file, argv);

    // FIXME: cleanup fork
    Error_add(error, strerror(errno));
    return IO_INVALID_FD;
}

int fork_exec_fd(char* file, char* argv[], int* pid, Error* error) {
    int is_tty = isatty(STDOUT_FILENO);

    if (is_tty == 0) {
        if (errno == EBADF) {
            Error_add(error, strerror(errno));
            return IO_INVALID_FD;
        }
        else {
            return fork_exec_pipe(file, argv, pid, error);
        }
    }
    else {
        return fork_exec_pty(file, argv, pid, error);
    }
}

// FIXME: http://stackoverflow.com/a/23428212/753501
int fork_exec_status(char* file, char* argv[], Error* error) {
    int child_pid = fork();

    if (child_pid == -1) {
        Error_add(error, strerror(errno));
        return -1;
    }
    else if (!child_pid) {
        int dev_null = open("/dev/null", O_RDWR);

        // FIXME: cleanup fork
        if (dup2(dev_null, STDERR_FILENO) == -1) {
            Error_add(error, strerror(errno));
            close(dev_null);
            return -1;
        }
        // FIXME: cleanup fork
        if (dup2(dev_null, STDOUT_FILENO) == -1) {
            Error_add(error, strerror(errno));
            close(dev_null);
            return -1;
        }

        execvp(file, argv);

        // FIXME: cleanup fork
        Error_add(error, strerror(errno));
        return -1;
    }
    else {
        int status;

        if (waitpid(child_pid, &status, 0) == -1) {
            Error_add(error, strerror(errno));
            return -1;
        }

        return WEXITSTATUS(status);
    }
}
