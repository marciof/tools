#include <errno.h>
#include <pty.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

int main(int argc, char* argv[]) {
    if (argc <= 1) {
        return EXIT_FAILURE;
    }

    int fd;
    pid_t pid = forkpty(&fd, NULL, NULL, NULL);

    if (pid == -1) {
        perror("forkpty");
        return EXIT_FAILURE;
    }
    else if (!pid) {
        execvp(argv[1], argv + 1);
        perror("execvp");
        _exit(EXIT_FAILURE);
    }
    else {
        uint8_t buffer[BUFSIZ];
        ssize_t nr_read;

        while ((nr_read = read(fd, buffer, BUFSIZ)) > 0) {
            size_t length = (size_t) nr_read;
            uint8_t* buffer_ptr = buffer;

            while (length > 0) {
                ssize_t nr_written = write(STDOUT_FILENO, buffer_ptr, length);

                if (nr_written == -1) {
                    perror("write");
                    return EXIT_FAILURE;
                }

                buffer_ptr += nr_written;
                length -= nr_written;
            }
        }

        if ((nr_read == -1) && (errno != EIO)) {
            perror("read");
            return EXIT_FAILURE;
        }

        if (close(fd) == -1) {
            perror("close");
            return EXIT_FAILURE;
        }

        int status;

        if (waitpid(pid, &status, 0) == -1) {
            perror("waitpid");
            return EXIT_FAILURE;
        }

        return WIFEXITED(status) ? WEXITSTATUS(status) : EXIT_FAILURE;
    }
}
