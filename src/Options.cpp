#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "iterator/Iterator.h"
#include "list/Array_List.h"
#include "Options.h"
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


Error ERROR_INVALID_OPTION = "Try '-h' for more information.";
Error ERROR_NO_PLUGIN_NAME = "No plugin name specified.";
Error ERROR_NO_PLUGIN_OPTION = "No plugin option specified.";


static void parse_plugin_option(char* option, Options* options, Error* error) {
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


void Options_delete(Options options) {
    std::map<char*, std::vector<char*>, Cstring_cmp>::iterator options_it
        = options.plugin_options.begin();

    for (; options_it != options.plugin_options.end(); ++options_it) {
        free(options_it->first);
    }

    Error discard;
    List_delete(options.disabled_plugins, &discard);
}


bool Options_is_plugin_enabled(
        Options options, const char* name, Error* error) {

    Iterator it = List_iterator(options.disabled_plugins, error);

    if (*error) {
        return false;
    }

    while (Iterator_has_next(it)) {
        const char* disabled_name = (const char*) Iterator_next(it, error);

        if (strcmp(disabled_name, name) == 0) {
            Iterator_delete(it);
            return false;
        }
    }

    Iterator_delete(it);
    return true;
}


Options Options_parse(int argc, char* argv[], Error* error) {
    Options options;
    int option;

    options.optind = -1;
    options.disabled_plugins = List_new(Array_List, error);

    if (*error) {
        return options;
    }

    while ((option = getopt(argc, argv, ALL_OPTS)) != -1) {
        if (option == *DISABLE_PLUGIN_OPT) {
            List_add(options.disabled_plugins, (intptr_t) optarg, error);

            if (*error) {
                Options_delete(options);
                return options;
            }
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
