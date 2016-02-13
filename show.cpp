#include <errno.h>
#include <pty.h>
#include <stdexcept>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <vector>


#define HELP_OPT "h"
#define PLUGIN_OPTION_OPT "p:"

#define ALL_OPTS ( \
    HELP_OPT \
    PLUGIN_OPTION_OPT \
)

#define ARRAY_LENGTH(array) \
    (sizeof(array) / sizeof((array)[0]))


namespace show {
    int exec_forkpty(char* file, std::vector<char*>* argv) {
        int saved_stderr = dup(STDERR_FILENO);

        if (saved_stderr == -1) {
            throw std::runtime_error(strerror(errno));
        }

        int child_out_fd;
        int child_pid = forkpty(&child_out_fd, NULL, NULL, NULL);

        if (child_pid == -1) {
            throw std::runtime_error(strerror(errno));
        }
        else if (child_pid != 0) {
            close(saved_stderr);
            return child_out_fd;
        }

        if (dup2(saved_stderr, STDERR_FILENO) == -1) {
            throw std::runtime_error(strerror(errno));
        }

        if (execvp(file, argv->data()) == -1) {
            throw std::runtime_error(strerror(errno));
        }
        else {
            exit(EXIT_SUCCESS);
        }
    }


    bool parse_options(int argc, char* argv[], std::vector<char*>* ls_options) {
        const char PLUGIN_OPTION_SEP[] = ":";
        int option;

        while ((option = getopt(argc, argv, ALL_OPTS)) != -1) {
            if (option == *PLUGIN_OPTION_OPT) {
                char* separator = strstr(optarg, PLUGIN_OPTION_SEP);

                if ((separator == NULL)
                    || (separator[ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1] == '\0'))
                {
                    throw std::runtime_error("No plugin option specified.");
                }

                unsigned long name_length = (separator - optarg);

                if (name_length == 0) {
                    throw std::runtime_error("No plugin name specified.");
                }

                if (strncmp("ls", optarg, name_length) == 0) {
                    ls_options->push_back(
                        separator + ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1);
                }
            }
            else if (option == *HELP_OPT) {
                fprintf(stderr,
                    "Usage: %s [OPTION]... [RESOURCE]...\n"
                        "Version: 0.1.0\n"
                        "\n"
                        "Options:\n"
                        "  -%c   plugin specific option, as PLUGIN:OPTION\n"
                        "  -%c   display this help and exit\n"
                        "\n"
                        "Plugins:\n"
                        "  ls   POSIX `ls` command\n",
                    argv[0],
                    *PLUGIN_OPTION_OPT,
                    *HELP_OPT);

                return false;
            }
            else {
                throw std::runtime_error("Try `-h` for more information.");
            }
        }

        for (int i = optind; i < argc; ++i) {
            ls_options->push_back(argv[i]);
        }

        return true;
    }
}


int main(int argc, char* argv[]) {
    std::vector<char*> ls_argv;
    ls_argv.push_back((char*) "ls");

    try {
        if (!show::parse_options(argc, argv, &ls_argv)) {
            return EXIT_SUCCESS;
        }
    }
    catch (const std::runtime_error& error) {
        fprintf(stderr, "%s\n", error.what());
        return EXIT_FAILURE;
    }

    ls_argv.push_back(NULL);
    int child_out_fd;

    try {
        child_out_fd = show::exec_forkpty(ls_argv[0], &ls_argv);
    }
    catch (const std::runtime_error& error) {
        fprintf(stderr, "%s\n", error.what());
        return EXIT_FAILURE;
    }

    ssize_t nr_bytes_read;
    const int BUFFER_SIZE = 256;
    char buffer[BUFFER_SIZE + 1];

    while ((nr_bytes_read = read(child_out_fd, buffer, BUFFER_SIZE)) > 0) {
        buffer[nr_bytes_read] = '\0';
        fputs(buffer, stdout);
    }

    return EXIT_SUCCESS;
}
