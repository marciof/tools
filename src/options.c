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
#define FIND_PLUGIN_FULL_NAME 0

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

        if (name_length != FIND_PLUGIN_FULL_NAME) {
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
        char* option,
        size_t plugins_length,
        Plugin* plugins[],
        size_t max_nr_options_per_plugin,
        size_t nr_options_per_plugin[],
        char* options_per_plugin[],
        Error* error) {

    char* separator = strstr(option, PLUGIN_OPT_SEP);

    bool is_option_missing
        = (separator == NULL)
        || (separator[C_ARRAY_LENGTH(PLUGIN_OPT_SEP) - 1] == '\0');

    if (is_option_missing) {
        Error_add(error, "no plugin option specified");
        Error_add(error, option);
        return;
    }

    size_t name_length = (separator - option);

    if (name_length == 0) {
        Error_add(error, "no plugin name specified");
        Error_add(error, option);
        return;
    }

    size_t pos = find_plugin(
        option, name_length, plugins_length, plugins, error);

    if (ERROR_HAS(error)) {
        Error_add(error, option);
        return;
    }

    char* value = separator + C_ARRAY_LENGTH(PLUGIN_OPT_SEP) - 1;

    options_per_plugin
        [pos * max_nr_options_per_plugin + nr_options_per_plugin[pos]]
        = value;

    ++nr_options_per_plugin[pos];
}

int parse_options(
        int argc,
        char* argv[],
        size_t plugins_length,
        Plugin* plugins[],
        size_t max_nr_options_per_plugin,
        size_t nr_options_per_plugin[],
        char* options_per_plugin[],
        Error* error) {

    int option;

    while ((option = getopt(argc, argv, ALL_OPTS)) != -1) {
        if (option == DISABLE_PLUGIN_OPT[0]) {
            size_t pos = find_plugin(
                optarg, FIND_PLUGIN_FULL_NAME, plugins_length, plugins, error);

            if (ERROR_HAS(error)) {
                return -1;
            }
            plugins[pos]->is_enabled = false;
        }
        else if (option == HELP_OPT[0]) {
            display_help(plugins, plugins_length);
            return -1;
        }
        else if (option == PLUGIN_OPTION_OPT[0]) {
            parse_plugin_option(
                optarg,
                plugins_length,
                plugins,
                max_nr_options_per_plugin,
                nr_options_per_plugin,
                options_per_plugin,
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
