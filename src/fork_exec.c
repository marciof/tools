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

static int fork_exec_pipe(
        char* file,
        char* argv[],
        int out_fd,
        int err_fd,
        int* pid,
        Error* error) {

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

        if (close(read_write_fds[1]) == -1) {
            Error_add(error, strerror(errno));
            return IO_INVALID_FD;
        }

        return read_write_fds[0];
    }
    else {
        bool has_failed =
            ((out_fd != STDOUT_FILENO)
                && (dup2(out_fd, STDOUT_FILENO) == -1))
            || ((err_fd != STDERR_FILENO)
                && (dup2(err_fd, STDERR_FILENO) == -1))
            || (execvp(file, argv) == -1);

        if (has_failed) {
            int saved_errno = errno;
            size_t remaining_length = sizeof(saved_errno);
            uint8_t* remaining_data = (uint8_t*) &saved_errno;

            // FIXME: refactor and merge with `io_write`?
            while (remaining_length > 0) {
                ssize_t bytes_written = write(
                    read_write_fds[1], remaining_data, remaining_length);

                if (bytes_written == -1) {
                    break;
                }

                remaining_length -= bytes_written;
                remaining_data += bytes_written;
            }
        }

        abort();
    }
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
    else {
        execvp(file, argv);

        // FIXME: cleanup fork
        Error_add(error, strerror(errno));
        return IO_INVALID_FD;
    }
}

int fork_exec_fd(char* file, char* argv[], int* pid, Error* error) {
    int is_tty = isatty(STDOUT_FILENO);

    if (is_tty == 1) {
        return fork_exec_pty(file, argv, pid, error);
    }
    else if (errno != EBADF) {
        return fork_exec_pipe(
            file, argv, STDOUT_FILENO, STDERR_FILENO, pid, error);
    }
    else {
        Error_add(error, strerror(errno));
        return IO_INVALID_FD;
    }
}

int fork_exec_status(char* file, char* argv[], Error* error) {
    int null_fd = open("/dev/null", O_RDWR);

    if (null_fd == -1) {
        Error_add(error, strerror(errno));
        return -1;
    }

    int child_pid;
    int read_fd = fork_exec_pipe(
        file, argv, null_fd, null_fd, &child_pid, error);

    if (ERROR_HAS(error)) {
        return -1;
    }

    int status;

    if (waitpid(child_pid, &status, 0) == -1) {
        Error_add(error, strerror(errno));
        return -1;
    }

    if (close(null_fd) == -1) {
        Error_add(error, strerror(errno));
        return -1;
    }

    if (!WIFEXITED(status)) {
        bool has_child_errno = io_has_input(read_fd, error);

        if (ERROR_HAS(error)) {
            return -1;
        }

        if (!has_child_errno) {
            Error_add(error, "Fork/exec subprocess did not exit normally");
        }
        else {
            int child_errno;
            size_t remaining_length = sizeof(child_errno);
            uint8_t* remaining_data = (uint8_t*) &child_errno;

            // FIXME: refactor into a `io_read`?
            while (remaining_length > 0) {
                ssize_t bytes_read = read(
                    read_fd, remaining_data, remaining_length);

                if (bytes_read == -1) {
                    Error_add(error, strerror(errno));
                    return -1;
                }

                remaining_length -= bytes_read;
                remaining_data += bytes_read;
            }

            Error_add(error, strerror(child_errno));
        }

        return -1;
    }

    return WEXITSTATUS(status);
}
