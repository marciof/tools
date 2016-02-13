#include <iostream>
#include <pty.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>


int main(int argc, char* argv[]) {
    int saved_stderr = dup(STDERR_FILENO);

    if (saved_stderr == -1) {
        perror("failed stderr dup");
        return EXIT_FAILURE;
    }

    int master_fd;
    int child_pid = forkpty(&master_fd, NULL, NULL, NULL);

    if (child_pid == -1) {
        perror("failed forkpty");
        return EXIT_FAILURE;
    }

    if (child_pid == 0) {
        if (dup2(saved_stderr, STDERR_FILENO) == -1) {
            perror("failed stderr restore");
            return -1;
        }

        char* child_argv[] = {
            (char*) "ls",
            NULL,
        };

        if (execvp("ls", child_argv) == -1) {
            perror("failed execvp");
            return EXIT_FAILURE;
        }
        else {
            return EXIT_SUCCESS;
        }
    }

    close(saved_stderr);

    ssize_t nr_bytes_read;
    const int BUFFER_SIZE = 256;
    char buffer[BUFFER_SIZE + 1];

    while ((nr_bytes_read = read(master_fd, buffer, BUFFER_SIZE)) > 0) {
        buffer[nr_bytes_read] = '\0';
        std::cout << buffer;
    }

    return EXIT_SUCCESS;
}
