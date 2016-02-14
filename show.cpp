#include <errno.h>
#include <map>
#include <pty.h>
#include <set>
#include <stdexcept>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <string.h>
#include <unistd.h>
#include <vector>


#define HELP_OPT "h"
#define DISABLE_PLUGIN_OPT "x:"
#define PLUGIN_OPTION_OPT "p:"

#define ALL_OPTS ( \
    HELP_OPT \
    DISABLE_PLUGIN_OPT \
    PLUGIN_OPTION_OPT \
)

#define ARRAY_LENGTH(array) \
    (sizeof(array) / sizeof((array)[0]))


using namespace std;


namespace show {
    int exec_forkpty(char* file, char* argv[]) {
        int saved_stderr = dup(STDERR_FILENO);

        if (saved_stderr == -1) {
            throw runtime_error(strerror(errno));
        }

        int child_out_fd;
        int child_pid = forkpty(&child_out_fd, NULL, NULL, NULL);

        if (child_pid == -1) {
            throw runtime_error(strerror(errno));
        }
        else if (child_pid != 0) {
            close(saved_stderr);
            return child_out_fd;
        }

        if (dup2(saved_stderr, STDERR_FILENO) == -1) {
            throw runtime_error(strerror(errno));
        }

        if (execvp(file, argv) == -1) {
            throw runtime_error(strerror(errno));
        }
        else {
            exit(EXIT_SUCCESS);
        }
    }


    void parse_plugin_option(
            char* option,
            map<string, vector<char*> >& plugin_options) {

        const char PLUGIN_OPTION_SEP[] = ":";
        char* separator = strstr(option, PLUGIN_OPTION_SEP);

        bool is_option_missing = (separator == NULL)
            || (separator[ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1] == '\0');

        if (is_option_missing) {
            throw runtime_error("No plugin option specified.");
        }

        unsigned long name_length = (separator - option);

        if (name_length == 0) {
            throw runtime_error("No plugin name specified.");
        }

        string name = string(option, name_length);
        auto options_it = plugin_options.find(name);

        vector<char*>& options = (options_it == plugin_options.end())
            ? plugin_options[name] = vector<char*>()
            : options_it->second;

        options.push_back(
            separator + ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1);
    }


    int parse_options(
            int argc,
            char* argv[],
            set<char*>& disabled_plugins,
            map<string, vector<char*> >& plugin_options) {

        int option;

        while ((option = getopt(argc, argv, ALL_OPTS)) != -1) {
            if (option == *DISABLE_PLUGIN_OPT) {
                disabled_plugins.insert(optarg);
            }
            else if (option == *HELP_OPT) {
                fprintf(stderr,
                    "Usage: show [OPTION]... [RESOURCE]...\n"
                        "Version: 0.2.0\n"
                        "\n"
                        "Options:\n"
                        "  -%c               display this help and exit\n"
                        "  -%c PLUGIN:OPT    pass an option to a plugin\n"
                        "  -%c PLUGIN        disable plugin\n"
                        "\n"
                        "Plugins:\n"
                        "  ls               POSIX `ls` command\n",
                    *HELP_OPT,
                    *PLUGIN_OPTION_OPT,
                    *DISABLE_PLUGIN_OPT);

                return -1;
            }
            else if (option == *PLUGIN_OPTION_OPT) {
                parse_plugin_option(optarg, plugin_options);
            }
            else {
                throw runtime_error("Try '-h' for more information.");
            }
        }

        return optind;
    }
}


int main(int argc, char* argv[]) {
    set<char*> disabled_plugins;
    map<string, vector<char*> > plugin_options;
    int arg_optind;

    try {
        arg_optind = show::parse_options(
            argc, argv, disabled_plugins, plugin_options);
    }
    catch (const runtime_error& error) {
        fprintf(stderr, "%s\n", error.what());
        return EXIT_FAILURE;
    }

    if (arg_optind < 0) {
        return EXIT_SUCCESS;
    }

    vector<char*> ls_argv;
    auto plugin_options_it = plugin_options.find("ls");

    ls_argv.push_back((char*) "ls");

    if (plugin_options_it != plugin_options.end()) {
        vector<char*>& options = plugin_options_it->second;
        ls_argv.insert(ls_argv.end(), options.begin(), options.end());
    }

    while (arg_optind < argc) {
        ls_argv.push_back(argv[arg_optind++]);
    }

    ls_argv.push_back(NULL);
    int child_out_fd;

    try {
        child_out_fd = show::exec_forkpty(ls_argv[0], ls_argv.data());
    }
    catch (const runtime_error& error) {
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
