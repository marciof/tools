#include <getopt.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "options.h"

#define PLUGIN_OPT_SEP "="

#define HELP_OPT "h"
#define DISABLE_PLUGIN_OPT "d:"
#define PLUGIN_OPTION_OPT "p:"

#define ALL_OPTS ( \
    HELP_OPT \
    DISABLE_PLUGIN_OPT \
    PLUGIN_OPTION_OPT \
)

#define ERROR_UNKNOWN_PLUGIN "no such plugin"
#define FIND_PLUGIN_BY_FULL_NAME 0

static void display_help(Plugin* plugins[], size_t nr_plugins) {
    fprintf(stderr,
        "Usage: show [OPTION]... [INPUT]...\n"
        "Version: 0.12.0\n"
        "\n"
        "Options:\n"
        "  -%c           display this help and exit\n"
        "  -%c NAME      disable a plugin\n"
        "  -%c NAME%sOPT  pass an option to a plugin\n",
        HELP_OPT[0],
        DISABLE_PLUGIN_OPT[0],
        PLUGIN_OPTION_OPT[0],
        PLUGIN_OPT_SEP);

    if (nr_plugins == 0) {
        return;
    }

    fputs("\nPlugins:\n", stderr);

    for (size_t i = 0; i < nr_plugins; ++i) {
        Plugin* plugin = plugins[i];

        fprintf(stderr, "  %-13s%s%s\n",
            plugin->name,
            plugin->description,
            plugin->is_available() ? "" : " (UNAVAILABLE)");
    }
}

static size_t find_plugin(
        char* name,
        size_t name_length,
        size_t nr_plugins,
        Plugin* plugins[],
        Error* error) {

    for (size_t i = 0; i < nr_plugins; ++i) {
        const char* other_name = plugins[i]->name;

        if (name_length != FIND_PLUGIN_BY_FULL_NAME) {
            size_t j = 0;

            for (j = 0; (j < name_length) && (other_name[j] != '\0'); ++j) {
                if (other_name[j] != name[j]) {
                    break;
                }
            }
            if (other_name[j] == '\0') {
                return i;
            }
        }
        else if (strcmp(other_name, name) == 0) {
            return i;
        }
    }

    Error_add(error, ERROR_UNKNOWN_PLUGIN);
    return 0;
}

static void parse_plugin_option(
        int argc,
        char* option,
        size_t nr_plugins,
        Plugin* plugins[],
        size_t plugins_nr_options[],
        char* plugins_options[],
        Error* error) {

    char* separator = strstr(option, PLUGIN_OPT_SEP);

    bool is_option_missing = (separator == NULL)
        || (separator[C_ARRAY_LENGTH(PLUGIN_OPT_SEP) - 1] == '\0');

    if (is_option_missing) {
        Error_add(error, "no plugin option specified");
        return;
    }

    size_t name_length = (separator - option);

    if (name_length == 0) {
        Error_add(error, "no plugin name specified");
        return;
    }

    size_t pos = find_plugin(
        option, name_length, nr_plugins, plugins, error);

    if (ERROR_HAS(error)) {
        return;
    }

    char* value = separator + C_ARRAY_LENGTH(PLUGIN_OPT_SEP) - 1;
    plugins_options[pos * argc + plugins_nr_options[pos]] = value;
    ++plugins_nr_options[pos];
}

int parse_options(
        int argc,
        char* argv[],
        size_t nr_plugins,
        Plugin* plugins[],
        size_t plugins_nr_options[],
        char* plugins_options[],
        Error* error) {

    int option;

    while ((option = getopt(argc, argv, ALL_OPTS)) != -1) {
        if (option == DISABLE_PLUGIN_OPT[0]) {
            size_t pos = find_plugin(
                optarg, FIND_PLUGIN_BY_FULL_NAME, nr_plugins, plugins, error);

            if (ERROR_HAS(error)) {
                return -1;
            }
            plugins[pos]->is_enabled = false;
        }
        else if (option == HELP_OPT[0]) {
            display_help(plugins, nr_plugins);
            return -1;
        }
        else if (option == PLUGIN_OPTION_OPT[0]) {
            parse_plugin_option(
                argc,
                optarg,
                nr_plugins,
                plugins,
                plugins_nr_options,
                plugins_options,
                error);

            if (ERROR_HAS(error)) {
                return -1;
            }
        }
        else {
            Error_add(error, "try '-" HELP_OPT "' for more information");
            return -1;
        }
    }

    return optind;
}
