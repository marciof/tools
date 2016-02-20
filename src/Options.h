#ifndef SHOW__OPTIONS_H
#define SHOW__OPTIONS_H


#include <map>
#include <stdbool.h>
#include <string.h>
#include <vector>
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
    std::map<char*, std::vector<char*>, Cstring_cmp> plugin_options;
} Options;


extern Error ERROR_INVALID_OPTION;
extern Error ERROR_NO_PLUGIN_NAME;
extern Error ERROR_NO_PLUGIN_OPTION;


void Options_delete(Options options);
bool Options_is_plugin_enabled(Options options, const char* name, Error* error);
Options Options_parse(int argc, char* argv[], Error* error);


#endif
