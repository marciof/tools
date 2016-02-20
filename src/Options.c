#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include "iterator/Iterator.h"
#include "list/Array_List.h"
#include "map/Hash_Map.h"
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


static void parse_plugin_option(Options options, char* option, Error* error) {
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

    if (*error) {
        return;
    }

    char* value = separator + STATIC_ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1;
    Error discard;

    List plugin_options = (List) Map_get(
        options.plugin_options, (intptr_t) name, &discard);

    if (plugin_options == NULL) {
        plugin_options = List_literal(Array_List, error, value, NULL);

        if (*error) {
            free(name);
            return;
        }

        Map_put(
            options.plugin_options,
            (intptr_t) name,
            (intptr_t) plugin_options,
            error);

        if (*error) {
            free(name);
            List_delete(plugin_options, &discard);
            return;
        }
    }
    else {
        free(name);
        List_add(plugin_options, (intptr_t) value, error);

        if (*error) {
            return;
        }
    }

    *error = NULL;
}


void Options_delete(Options options) {
    Error discard;
    Iterator it = Map_keys_iterator(options.plugin_options, &discard);

    if (!discard) {
        while (Iterator_has_next(it)) {
            char* plugin_name = (char*) Iterator_next(it, &discard);

            List plugin_options = (List) Map_get(
                options.plugin_options, (intptr_t) plugin_name, &discard);

            free(plugin_name);
            List_delete(plugin_options, &discard);
        }

        Iterator_delete(it);
    }

    Map_delete(options.plugin_options, &discard);
    List_delete(options.disabled_plugins, &discard);
}


List Options_get_plugin_options(Options options, const char* name) {
    Error discard;
    return (List) Map_get(options.plugin_options, (intptr_t) name, &discard);
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
    int option;
    Options options = {
        -1,
        NULL,
        NULL,
    };

    options.optind = -1;
    options.disabled_plugins = List_new(Array_List, error);

    if (*error) {
        return options;
    }

    options.plugin_options = Map_new(Hash_Map, error);

    if (*error) {
        Options_delete(options);
        return options;
    }

    Map_set_property(
        options.plugin_options,
        HASH_MAP_EQUAL,
        (intptr_t) Hash_Map_str_equal,
        error);

    Map_set_property(
        options.plugin_options,
        HASH_MAP_HASH,
        (intptr_t) Hash_Map_str_hash,
        error);

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
            parse_plugin_option(options, optarg, error);

            if (*error) {
                Options_delete(options);
                return options;
            }
        }
        else {
            Options_delete(options);
            *error = "Try '-h' for more information.";
            return options;
        }
    }

    *error = NULL;
    options.optind = optind;
    return options;
}
