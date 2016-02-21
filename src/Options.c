#include <getopt.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
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


static void display_help(Plugin* plugins[], size_t nr_plugins) {
    fprintf(stderr,
        "Usage: show [OPTION]... [RESOURCE]...\n"
        "Version: 0.3.0\n"
        "\n"
        "Options:\n"
        "  -%c              display this help and exit\n"
        "  -%c PLUGIN:OPT   pass an option to a plugin\n"
        "  -%c PLUGIN       disable plugin\n",
        *HELP_OPT,
        *PLUGIN_OPTION_OPT,
        *DISABLE_PLUGIN_OPT);

    if (nr_plugins > 0) {
        bool needs_header = true;

        for (size_t i = 0; i < nr_plugins; ++i) {
            if (!plugins[i]) {
                continue;
            }

            if (needs_header) {
                needs_header = false;

                fputs(
                    "\n"
                    "Plugins:\n",
                    stderr);
            }

            fprintf(stderr, "  %-16s%s\n",
                plugins[i]->get_name(),
                plugins[i]->get_description());
        }
    }
}


static void parse_plugin_option(
        char* option,
        Plugin* plugins[],
        size_t nr_plugins,
        Error* error) {

    const char PLUGIN_OPTION_SEP[] = ":";
    char* separator = strstr(option, PLUGIN_OPTION_SEP);

    bool is_option_missing = (separator == NULL)
        || (separator[STATIC_ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1] == '\0');

    if (is_option_missing) {
        *error = "No plugin option specified.";
        return;
    }

    size_t name_length = (separator - option);

    if (name_length == 0) {
        *error = "No plugin name specified.";
        return;
    }

    char* name = strncopy((const char*) option, name_length, error);
    Plugin* plugin = NULL;

    if (*error) {
        return;
    }

    for (size_t i = 0; i < nr_plugins; ++i) {
        if (plugins[i] && strcmp(name, plugins[i]->get_name()) == 0) {
            plugin = plugins[i];
            break;
        }
    }

    free(name);

    if (plugin == NULL) {
        *error = "No such plugin or disabled.";
        return;
    }

    char* value = separator + STATIC_ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1;

    if (plugin->options == NULL) {
        plugin->options = List_literal(Array_List, error, value, NULL);

        if (*error) {
            return;
        }
    }
    else {
        List_add(plugin->options, (intptr_t) value, error);

        if (*error) {
            return;
        }
    }

    *error = NULL;
}


int Options_parse(
        int argc,
        char* argv[],
        Plugin* plugins[],
        size_t nr_plugins,
        Error* error) {

    int option;

    while ((option = getopt(argc, argv, ALL_OPTS)) != -1) {
        if (option == *DISABLE_PLUGIN_OPT) {
            for (size_t i = 0; i < nr_plugins; ++i) {
                if (plugins[i] && strcmp(optarg, plugins[i]->get_name()) == 0) {
                    Error discard;
                    List_delete(plugins[i]->options, &discard);
                    plugins[i] = NULL;
                    break;
                }
            }
        }
        else if (option == *HELP_OPT) {
            display_help(plugins, nr_plugins);
            *error = NULL;
            return -1;
        }
        else if (option == *PLUGIN_OPTION_OPT) {
            parse_plugin_option(optarg, plugins, nr_plugins, error);

            if (*error) {
                return -1;
            }
        }
        else {
            *error = "Try '-h' for more information.";
            return -1;
        }
    }

    *error = NULL;
    return optind;
}
