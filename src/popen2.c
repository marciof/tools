#include <errno.h>
#include <fcntl.h>
#include <pty.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>
#include "io.h"
#include "popen2.h"

#define EXECVP_ENOENT_FAILED_SIGNAL SIGUSR1

static int popen2_pipe(
        char* file,
        char* argv[],
        bool is_read,
        int out_fd,
        int err_fd,
        pid_t* pid,
        Error* error) {

    int rw_fds[2];

    if (pipe(rw_fds) == -1) {
        Error_add(error, strerror(errno));
        return IO_NULL_FD;
    }

    pid_t child_pid = fork();

    if (child_pid == -1) {
        Error_add(error, strerror(errno));
        return IO_NULL_FD;
    }
    else if (child_pid) {
        int fd_close = is_read ? rw_fds[1] : rw_fds[0];
        int fd_return = is_read ? rw_fds[0] : rw_fds[1];

        if (close(fd_close) == -1) {
            Error_add(error, strerror(errno));
            return IO_NULL_FD;
        }

        *pid = child_pid;
        return fd_return;
    }
    else {
        bool has_failed = (
            ((out_fd != IO_NULL_FD) && (dup2(out_fd, STDOUT_FILENO) == -1))
            || ((err_fd != IO_NULL_FD) && (dup2(err_fd, STDERR_FILENO) == -1))
            || (!is_read && (dup2(rw_fds[0], STDIN_FILENO) == -1))
            || (close(rw_fds[0]) == -1)
            || (close(rw_fds[1]) == -1));

        if (!has_failed) {
            execvp(file, argv);

            if (errno == ENOENT) {
                raise(EXECVP_ENOENT_FAILED_SIGNAL);
            }
        }

        // Don't use `exit` to avoid duplicate cleanups.
        abort();
    }
}

// Can only be used for reading, since input is interpreted as TTY/user input.
static int popen2_pty(
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
        return IO_NULL_FD;
    }
    else if (child_pid) {
        *pid = child_pid;
        return child_fd_out;
    }
    else {
        bool has_failed =
            ((out_fd != IO_NULL_FD) && (dup2(out_fd, STDOUT_FILENO) == -1))
            || ((err_fd != IO_NULL_FD) && (dup2(err_fd, STDERR_FILENO) == -1));

        if (!has_failed) {
            execvp(file, argv);

            if (errno == ENOENT) {
                raise(EXECVP_ENOENT_FAILED_SIGNAL);
            }
        }

        // Don't use `exit` to avoid duplicate cleanups.
        abort();
    }
}

int popen2(
        char* file,
        char* argv[],
        bool is_read,
        int out_fd,
        int err_fd,
        pid_t* pid,
        Error* error) {

    if (is_read) {
        bool is_tty = io_is_tty(STDOUT_FILENO, error);

        if (ERROR_HAS(error)) {
            Error_add(error, strerror(errno));
            return IO_NULL_FD;
        }

        if (is_tty) {
            return popen2_pty(file, argv, out_fd, err_fd, pid, error);
        }
    }

    return popen2_pipe(file, argv, is_read, out_fd, err_fd, pid, error);
}

bool popen2_can_run(char* file, Error* error) {
    char* argv[] = {file, NULL};
    popen2_status(file, argv, error);

    if (ERROR_HAS(error)) {
        if (strcmp(ERROR_GET_LAST(error), strerror(ENOENT)) == 0) {
            ERROR_CLEAR(error);
        }
        return false;
    }

    return true;
}

int popen2_status(char* file, char* argv[], Error* error) {
    int discard_fd = open("/dev/null", O_RDWR);

    if (discard_fd == -1) {
        Error_add(error, strerror(errno));
        return -1;
    }

    pid_t child_pid;
    popen2(file, argv, true, discard_fd, discard_fd, &child_pid, error);

    if (ERROR_HAS(error)) {
        close(discard_fd);
        return -1;
    }

    int status = wait_subprocess(child_pid, error);

    if (ERROR_HAS(error)) {
        close(discard_fd);
        return -1;
    }

    if (close(discard_fd) == -1) {
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

    if (WIFSIGNALED(status)) {
        int child_signal = WTERMSIG(status);

        if (child_signal == EXECVP_ENOENT_FAILED_SIGNAL) {
            Error_add(error, strerror(ENOENT));
            return -1;
        }
    }

    if (!WIFEXITED(status)) {
        Error_add(error, "Subprocess did not exit normally");
        return -1;
    }

    return WEXITSTATUS(status);
}
