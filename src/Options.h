#ifndef SHOW__OPTIONS_H
#define SHOW__OPTIONS_H


#include <map>
#include <stdbool.h>
#include <string.h>
#include "list/List.h"
#include "std/Error.h"


struct Cstring_cmp {
    bool operator()(char* a, char* b) const {
        return strcmp(a, b) < 0;
    }
};


typedef struct {
    int optind;
    List disabled_plugins;
    std::map<char*, List, Cstring_cmp>* plugin_options;
} Options;


void Options_delete(Options options);
List Options_get_plugin_options(Options options, const char* name);
bool Options_is_plugin_enabled(Options options, const char* name, Error* error);
Options Options_parse(int argc, char* argv[], Error* error);


#endif
