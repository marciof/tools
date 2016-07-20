#include <errno.h>
#include <fcntl.h>
#include <pty.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>
#include "fork_exec.h"
#include "io.h"

static void init_child_failure_pipe(int read_write_fds[2], Error* error) {
    if (pipe(read_write_fds) == -1) {
        Error_add(error, strerror(errno));
    }
    else if (fcntl(read_write_fds[0], F_SETFL, O_NONBLOCK) == -1) {
        Error_add(error, strerror(errno));

        if (close(read_write_fds[0]) == -1) {
            Error_add(error, strerror(errno));
        }
        if (close(read_write_fds[1]) == -1) {
            Error_add(error, strerror(errno));
        }
    }
}

static bool is_set_child_failure_pipe(int read_write_fds[2], Error* error) {
    uint8_t has_failed = 0;

    if ((read(read_write_fds[0], &has_failed, 1) == -1) && (errno != EAGAIN)) {
        Error_add(error, strerror(errno));
        return false;
    }
    else {
        return has_failed == 1;
    }
}

static void set_child_failure_pipe(int read_write_fds[2], Error* error) {
    uint8_t has_failed = 1;

    while (true) {
        ssize_t nr_bytes_read = write(read_write_fds[1], &has_failed, 1);

        if (nr_bytes_read == -1) {
            Error_add(error, strerror(errno));
            break;
        }
        else if (nr_bytes_read == 1) {
            break;
        }
    }
}

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

    if (is_tty == 1) {
        return fork_exec_pty(file, argv, pid, error);
    }
    else if (errno != EBADF) {
        return fork_exec_pipe(file, argv, pid, error);
    }
    else {
        Error_add(error, strerror(errno));
        return IO_INVALID_FD;
    }
}

// FIXME: refactor into and wrap `fork_exec_pipe`?
int fork_exec_status(char* file, char* argv[], Error* error) {
    int read_write_fds[2];
    init_child_failure_pipe(read_write_fds, error);

    if (ERROR_HAS(error)) {
        return -1;
    }

    int child_pid = fork();

    if (child_pid == -1) {
        Error_add(error, strerror(errno));
        return -1;
    }
    else if (!child_pid) {
        int dev_null;

        bool has_failed = ((dev_null = open("/dev/null", O_RDWR)) == -1)
            || (dup2(dev_null, STDERR_FILENO) == -1)
            || (dup2(dev_null, STDOUT_FILENO) == -1)
            || (execvp(file, argv) == -1);

        if (has_failed) {
            int saved_errno = errno;
            set_child_failure_pipe(read_write_fds, error);
            Error_print(error, stderr);
            errno = saved_errno;
        }

        exit(errno);
    }
    else {
        int status;

        if (waitpid(child_pid, &status, 0) == -1) {
            Error_add(error, strerror(errno));
            return -1;
        }

        bool has_failed = is_set_child_failure_pipe(read_write_fds, error);

        if (ERROR_HAS(error)) {
            return -1;
        }
        if (!WIFEXITED(status)) {
            Error_add(error, "Fork/exec subprocess did not exit");
            return -1;
        }

        int exit_status = WEXITSTATUS(status);

        if (has_failed) {
            Error_add(error, strerror(exit_status));
            return -1;
        }

        return exit_status;
    }
}
