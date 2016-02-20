#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "options.h"
#include "std/array.h"
#include "std/string.h"


#define HELP_OPT "h"
#define DISABLE_PLUGIN_OPT "x:"
#define PLUGIN_OPTION_OPT "p:"

#define ALL_OPTS ( \
    HELP_OPT \
    DISABLE_PLUGIN_OPT \
    PLUGIN_OPTION_OPT \
)


char* ERROR_INVALID_OPTION = (char*) "Try '-h' for more information.";
char* ERROR_NO_PLUGIN_NAME = (char*) "No plugin name specified.";
char* ERROR_NO_PLUGIN_OPTION = (char*) "No plugin option specified.";


static void parse_plugin_option(char* option, Options* options, char** error) {
    const char PLUGIN_OPTION_SEP[] = ":";
    char* separator = strstr(option, PLUGIN_OPTION_SEP);

    bool is_option_missing = (separator == NULL)
        || (separator[STATIC_ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1] == '\0');

    if (is_option_missing) {
        *error = ERROR_NO_PLUGIN_OPTION;
        return;
    }

    size_t name_length = (separator - option);

    if (name_length == 0) {
        *error = ERROR_NO_PLUGIN_NAME;
        return;
    }

    char* name = strncopy((const char*) option, name_length, error);

    if (*error) {
        return;
    }

    char* value = separator + STATIC_ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1;

    std::map<char*, std::vector<char*>, Cstring_cmp>::iterator it
        = options->plugin_options.find(name);

    if (it == options->plugin_options.end()) {
        options->plugin_options[name] = std::vector<char*>(1, value);
    }
    else {
        free(name);
        it->second.push_back(value);
    }

    *error = NULL;
}


Options Options_parse(int argc, char* argv[], char** error) {
    Options options;
    int option;

    options.optind = -1;

    while ((option = getopt(argc, argv, ALL_OPTS)) != -1) {
        if (option == *DISABLE_PLUGIN_OPT) {
            options.disabled_plugins.insert(optarg);
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

            *error = NULL;
            return options;
        }
        else if (option == *PLUGIN_OPTION_OPT) {
            parse_plugin_option(optarg, &options, error);

            if (*error) {
                return options;
            }
        }
        else {
            *error = ERROR_INVALID_OPTION;
            return options;
        }
    }

    *error = NULL;
    options.optind = optind;
    return options;
}
