#ifndef __MAIN__
#define __MAIN__


#include <eon/library/features.h>


#define PLUGIN_NAME "libPurple"

#define PLUGIN_DESCRIPTION "libPurple interface wrapper."

#define PLUGIN_MIME_TYPE "application/x-libpurple"

#define PLUGIN_MAJOR_VERSION 2011

#define PLUGIN_MINOR_VERSION 10

#define PLUGIN_MICRO_VERSION 06

#define PLUGIN_VERSION \
    TO_STRING_INDIRECT(PLUGIN_MAJOR_VERSION) "-" \
    TO_STRING_INDIRECT(PLUGIN_MINOR_VERSION) "-" \
    TO_STRING_INDIRECT(PLUGIN_MICRO_VERSION)


#endif
