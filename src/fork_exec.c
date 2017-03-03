#include <errno.h>
#include <fcntl.h>
#include <pty.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>
#include "fork_exec.h"
#include "io.h"

static int fork_exec_fd_pty(
        char* file,
        char* argv[],
        int out_fd,
        int err_fd,
        pid_t* pid,
        Error* error) {

    int child_fd_out;
    pid_t child_pid = forkpty(&child_fd_out, NULL, NULL, NULL);

    if (child_pid == -1) {
        Error_add(error, strerror(errno));
        return IO_INVALID_FD;
    }
    else if (child_pid) {
        *pid = child_pid;
        return child_fd_out;
    }
    else {
        bool has_failed =
            ((out_fd != IO_INVALID_FD)
                && (dup2(out_fd, STDOUT_FILENO) == -1))
            || ((err_fd != IO_INVALID_FD)
                && (dup2(err_fd, STDERR_FILENO) == -1));

        if (has_failed) {
            Error_add(error, strerror(errno));
            return IO_INVALID_FD;
        }

        execvp(file, argv);
        abort();
    }
}

int fork_exec_fd(
        char* file,
        char* argv[],
        int out_fd,
        int err_fd,
        pid_t* pid,
        Error* error) {

    if (isatty(STDOUT_FILENO)) {
        return fork_exec_fd_pty(file, argv, out_fd, err_fd, pid, error);
    }
    else if (errno != EBADF) {
        return fork_exec_fd_pipe(file, argv, out_fd, err_fd, true, pid, error);
    }
    else {
        Error_add(error, strerror(errno));
        return IO_INVALID_FD;
    }
}

int fork_exec_fd_pipe(
        char* file,
        char* argv[],
        int out_fd,
        int err_fd,
        bool is_for_reading,
        pid_t* pid,
        Error* error) {

    int read_write_fds[2];

    if (pipe(read_write_fds) == -1) {
        Error_add(error, strerror(errno));
        return IO_INVALID_FD;
    }

    pid_t child_pid = fork();

    if (child_pid == -1) {
        Error_add(error, strerror(errno));
        return IO_INVALID_FD;
    }
    else if (child_pid) {
        int fd_close = is_for_reading ? read_write_fds[1] : read_write_fds[0];
        int fd_return = is_for_reading ? read_write_fds[0] : read_write_fds[1];

        if (close(fd_close) == -1) {
            Error_add(error, strerror(errno));
            return IO_INVALID_FD;
        }

        *pid = child_pid;
        return fd_return;
    }
    else {
        bool has_failed;

        if (is_for_reading) {
            has_failed =
                ((out_fd != IO_INVALID_FD)
                 && (dup2(out_fd, STDOUT_FILENO) == -1))
                || ((err_fd != IO_INVALID_FD)
                    && (dup2(err_fd, STDERR_FILENO) == -1));
        }
        else {
            has_failed =
                (close(read_write_fds[1]) == -1)
                || ((read_write_fds[0] != STDIN_FILENO)
                    && (dup2(read_write_fds[0], STDIN_FILENO) == -1));
        }

        if (has_failed) {
            Error_add(error, strerror(errno));
            return IO_INVALID_FD;
        }

        execvp(file, argv);
        abort();
    }
}

int fork_exec_status(char* file, char* argv[], Error* error) {
    int null_fd = open("/dev/null", O_RDWR);

    if (null_fd == -1) {
        Error_add(error, strerror(errno));
        return -1;
    }

    pid_t child_pid;
    fork_exec_fd(file, argv, null_fd, null_fd, &child_pid, error);

    if (ERROR_HAS(error)) {
        return -1;
    }

    int status = wait_subprocess(child_pid, error);

    if (ERROR_HAS(error)) {
        close(null_fd);
        return -1;
    }

    if (close(null_fd) == -1) {
        Error_add(error, strerror(errno));
        return -1;
    }

    return status;
}

int wait_subprocess(pid_t child_pid, Error* error) {
    int status;

    if ((waitpid(child_pid, &status, 0) == -1) && (errno != ECHILD)) {
        Error_add(error, strerror(errno));
        return -1;
    }

    if (!WIFEXITED(status)) {
        Error_add(error, "Subprocess did not exit normally");
        return -1;
    }

    return WEXITSTATUS(status);
}
