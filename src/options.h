#ifndef SHOW__OPTIONS_H
#define SHOW__OPTIONS_H


#include <map>
#include <set>
#include <stdbool.h>
#include <string.h>
#include <vector>
#include "std/Error.h"


struct Cstring_cmp {
    bool operator()(char* a, char* b) const {
        return strcmp(a, b) < 0;
    }
};


typedef struct {
    int optind;
    std::set<char*, Cstring_cmp> disabled_plugins;
    std::map<char*, std::vector<char*>, Cstring_cmp> plugin_options;
} Options;


extern Error ERROR_INVALID_OPTION;
extern Error ERROR_NO_PLUGIN_NAME;
extern Error ERROR_NO_PLUGIN_OPTION;


void Options_delete(Options options);
Options Options_parse(int argc, char* argv[], Error* error);


#endif
