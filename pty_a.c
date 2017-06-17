#define _DEFAULT_SOURCE
#define _POSIX_C_SOURCE

#include <errno.h>
#include <pty.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/select.h>
#include <sys/types.h>
#include <termios.h>
#include <unistd.h>

static struct termios old_stdin_term;
static pid_t child_pid = -1;

static void reset_stdin_term() {
    // FIXME: check all requested changes were successfully carried out
    if (tcsetattr(STDIN_FILENO, TCSANOW, &old_stdin_term) == -1) {
        perror("tcsetattr");
        exit(EXIT_FAILURE);
    }
}

static bool flush(int from_fd, int to_fd) {
    uint8_t buffer[BUFSIZ];
    ssize_t bytes_read = read(from_fd, buffer, sizeof(buffer));

    // FIXME: handle `EIO`
    if (bytes_read <= 0) {
        return false;
    }

    uint8_t* buffer_ptr = buffer;

    while (bytes_read > 0) {
        ssize_t bytes_written = write(to_fd, buffer_ptr, (size_t) bytes_read);

        if (bytes_written == -1) {
            perror("write");
            reset_stdin_term();
            exit(EXIT_FAILURE);
        }

        buffer_ptr += bytes_written;
        bytes_read -= bytes_written;
    }

    return true;
}

static void forward_signal(int signal) {
    if (kill(child_pid, signal) == -1) {
        perror("kill");
        reset_stdin_term();
        exit(EXIT_FAILURE);
    }
}

static bool setup_signal(int signal) {
    struct sigaction new_sigaction;

    sigemptyset(&new_sigaction.sa_mask);
    new_sigaction.sa_handler = forward_signal;
    new_sigaction.sa_flags = 0;

    if (sigaction(signal, &new_sigaction, NULL) == -1) {
        perror("sigaction");
        return false;
    }

    return true;
}

int main(int argc, char* argv[]) {
    if (argc <= 1) {
        return EXIT_FAILURE;
    }

    int pty_fd;
    child_pid = forkpty(&pty_fd, NULL, NULL, NULL);

    if (child_pid == -1) {
        perror("forkpty");
        return EXIT_FAILURE;
    }

    if (!child_pid) {
        execvp(argv[1], argv + 1);
        perror("execvp");
        abort();
    }

    // FIXME: handle Ctrl+Z
    if (!setup_signal(SIGINT) || !setup_signal(SIGTSTP)) {
        return EXIT_FAILURE;
    }

    if (tcgetattr(STDIN_FILENO, &old_stdin_term) == -1) {
        perror("tcgetattr");
        return EXIT_FAILURE;
    }

    static struct termios new_stdin_term;
    new_stdin_term = old_stdin_term;

    // FIXME: terminal size
    cfmakeraw(&new_stdin_term);

    // FIXME: check all requested changes were successfully carried out
    if (tcsetattr(STDIN_FILENO, TCSANOW, &new_stdin_term) == -1) {
        perror("tcsetattr");
        return EXIT_FAILURE;
    }

    bool is_running = true;

    while (is_running) {
        fd_set fds;

        FD_ZERO(&fds);
        FD_SET(pty_fd, &fds);
        FD_SET(STDIN_FILENO, &fds);

        int max_fd = (pty_fd > STDIN_FILENO) ? pty_fd : STDIN_FILENO;

        if (select(max_fd + 1, &fds, NULL, NULL, NULL) == -1) {
            if (errno == EINTR) {
                continue;
            }
            perror("select");
            reset_stdin_term();
            return EXIT_FAILURE;
        }

        if (FD_ISSET(STDIN_FILENO, &fds) && !flush(STDIN_FILENO, pty_fd)) {
            is_running = false;
        }

        if (FD_ISSET(pty_fd, &fds) && !flush(pty_fd, STDOUT_FILENO)) {
            is_running = false;
        }
    }

    reset_stdin_term();
    return EXIT_SUCCESS;
}
