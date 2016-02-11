#include <iostream>
#include <pty.h>
#include <stdlib.h>
#include <unistd.h>


int main(int argc, char* argv[]) {
    int master_fd;
    int child_pid = forkpty(&master_fd, NULL, NULL, NULL);

    if (child_pid == -1) {
        std::cout << "failed forkpty" << std::endl;
        return EXIT_FAILURE;
    }

    if (child_pid == 0) {
        char* child_argv[] = {
            (char*) "ls",
            NULL,
        };

        if (execvp("ls", child_argv) == -1) {
            std::cout << "failed execvp" << std::endl;
            return EXIT_FAILURE;
        }
        else {
            return EXIT_SUCCESS;
        }
    }

    int nr_bytes;
    char buffer[256];

    while ((nr_bytes = read(master_fd, buffer, 256)) > 0) {
        buffer[nr_bytes] = '\0';
        std::cout << buffer;
    }

    return EXIT_SUCCESS;
}
