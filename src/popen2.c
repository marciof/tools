#include <fcntl.h>
#include <signal.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>
#include "io.h"
#include "popen2.h"

#ifdef __APPLE__
    #include <util.h>
#else
    #include <pty.h>
#endif

#define EXECVP_ENOENT_FAILED_SIGNAL SIGUSR1

static int popen2_pipe(
        char* file,
        char* argv[],
        bool is_read,
        int out_fd,
        int err_fd,
        pid_t* pid,
        struct Error* error) {

    int rw_fds[2];

    if (pipe(rw_fds) == -1) {
        Error_add_errno(error, errno);
        return IO_NULL_FD;
    }

    pid_t child_pid = fork();

    if (child_pid == -1) {
        Error_add_errno(error, errno);
        return IO_NULL_FD;
    }
    else if (child_pid) {
        int fd_close = is_read ? rw_fds[1] : rw_fds[0];
        int fd_return = is_read ? rw_fds[0] : rw_fds[1];

        if (close(fd_close) == -1) {
            Error_add_errno(error, errno);
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
        struct Error* error) {

    int child_fd_out;
    pid_t child_pid = forkpty(&child_fd_out, NULL, NULL, NULL);

    if (child_pid == -1) {
        Error_add_errno(error, errno);
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
        struct Error* error) {

    if (is_read) {
        bool is_tty = io_is_tty(STDOUT_FILENO, error);

        if (Error_has(error)) {
            Error_add_errno(error, errno);
            return IO_NULL_FD;
        }

        if (is_tty) {
            return popen2_pty(file, argv, out_fd, err_fd, pid, error);
        }
    }

    return popen2_pipe(file, argv, is_read, out_fd, err_fd, pid, error);
}

bool popen2_check(char* file, char* argv[], struct Error* error) {
    int status = popen2_status(file, argv, error);

    if (Error_has_errno(error, ENOENT)) {
        Error_clear(error);
        return false;
    }

    return !Error_has(error) && (status == 0);
}

void popen2_close(int fd, pid_t child_pid, struct Error* error) {
    if (close(fd) == -1) {
        Error_add_errno(error, errno);
        return;
    }

    int status = popen2_wait(child_pid, error);

    if (Error_has_errno(error, ENOENT)) {
        return;
    }

    if (!Error_has(error) && (status != 0)) {
        Error_add_string(error, "subprocess exited with an error code");
    }
}

int popen2_status(char* file, char* argv[], struct Error* error) {
    int discard_fd = open("/dev/null", O_RDWR);

    if (discard_fd == -1) {
        Error_add_errno(error, errno);
        return -1;
    }

    pid_t child_pid;

    int fd = popen2(
        file, argv, true, discard_fd, discard_fd, &child_pid, error);

    if (Error_has(error)) {
        close(discard_fd);
        return -1;
    }

    ssize_t bytes_read;
    uint8_t buffer[BUFSIZ];
    while ((bytes_read = read(fd, buffer, BUFSIZ)) > 0);

    if ((bytes_read == -1) && (errno != EIO)) {
        Error_add_errno(error, errno);
        close(discard_fd);
        return -1;
    }

    int status = popen2_wait(child_pid, error);

    if (Error_has(error)) {
        close(discard_fd);
        return -1;
    }

    if (close(discard_fd) == -1) {
        Error_add_errno(error, errno);
        return -1;
    }

    return status;
}

int popen2_wait(pid_t child_pid, struct Error* error) {
    int status;

    if (waitpid(child_pid, &status, 0) == -1) {
        Error_add_errno(error, errno);
        return -1;
    }

    if (WIFSIGNALED(status)) {
        int child_signal = WTERMSIG(status);

        if (child_signal == EXECVP_ENOENT_FAILED_SIGNAL) {
            Error_add_errno(error, ENOENT);
            return -1;
        }
    }

    if (!WIFEXITED(status)) {
        Error_add_string(error, "subprocess did not exit normally");
        return -1;
    }

    return WEXITSTATUS(status);
}
