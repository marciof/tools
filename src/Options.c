#include <getopt.h>
#include <stddef.h>
#include <stdio.h>
#include <sys/types.h>
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

#define ERROR_UNKNOWN_PLUGIN "No such plugin or disabled."


static void display_help(Plugin* plugins[], size_t nr_plugins) {
    fprintf(stderr,
        "Usage: show [OPTION]... [RESOURCE]...\n"
        "Version: 0.4.0\n"
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


static ssize_t find_plugin(
        char* name,
        size_t name_length,
        Plugin* plugins[],
        size_t nr_plugins) {

    for (size_t i = 0; i < nr_plugins; ++i) {
        if (plugins[i]) {
            const char* other = plugins[i]->get_name();

            if (name_length == 0) {
                if (strcmp(other, name) == 0) {
                    return i;
                }
            }
            else {
                size_t j = 0;

                for (j = 0; (j < name_length) && (other[j] != '\0'); ++j) {
                    if (other[j] != name[j]) {
                        break;
                    }
                }

                if (j == name_length) {
                    return i;
                }
            }
        }
    }

    return -1;
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
        Error_set(error, "No plugin option specified.");
        return;
    }

    size_t name_length = (separator - option);

    if (name_length == 0) {
        Error_set(error, "No plugin name specified.");
        return;
    }

    ssize_t plugin_pos = find_plugin(option, name_length, plugins, nr_plugins);

    if (plugin_pos < 0) {
        Error_set(error, ERROR_UNKNOWN_PLUGIN);
        return;
    }

    Plugin* plugin = plugins[plugin_pos];
    char* value = separator + STATIC_ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1;

    if (plugin->options == NULL) {
        plugin->options = List_new(error, value, NULL);

        if (Error_has(error)) {
            return;
        }
    }
    else {
        List_add(plugin->options, (intptr_t) value, error);

        if (Error_has(error)) {
            return;
        }
    }

    Error_clear(error);
}


List Options_parse(
        int argc,
        char* argv[],
        Plugin* plugins[],
        size_t nr_plugins,
        Error* error) {

    int option;

    while ((option = getopt(argc, argv, ALL_OPTS)) != -1) {
        if (option == *DISABLE_PLUGIN_OPT) {
            ssize_t pos = find_plugin(optarg, 0, plugins, nr_plugins);

            if (pos >= 0) {
                List_delete(plugins[pos]->options, NULL);
                plugins[pos] = NULL;
            }
            else {
                Error_set(error, ERROR_UNKNOWN_PLUGIN);
                return NULL;
            }
        }
        else if (option == *HELP_OPT) {
            display_help(plugins, nr_plugins);
            Error_clear(error);
            return NULL;
        }
        else if (option == *PLUGIN_OPTION_OPT) {
            parse_plugin_option(optarg, plugins, nr_plugins, error);

            if (Error_has(error)) {
                return NULL;
            }
        }
        else {
            Error_set(error, "Try '-h' for more information.");
            return NULL;
        }
    }

    List args = List_new(error, NULL);

    if (Error_has(error)) {
        return NULL;
    }

    for (int i = optind; i < argc; ++i) {
        List_add(args, (intptr_t) argv[i], error);

        if (Error_has(error)) {
            List_delete(args, NULL);
            return NULL;
        }
    }

    Error_clear(error);
    return args;
}
