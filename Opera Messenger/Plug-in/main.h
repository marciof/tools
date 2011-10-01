#ifndef __MAIN__
#define __MAIN__


#define PLUGIN_NAME "libPurple"

#define PLUGIN_DESCRIPTION "libPurple interface wrapper."

#define PLUGIN_MIME_TYPE "application/x-libpurple"

#define PLUGIN_MAJOR_VERSION 2011

#define PLUGIN_MINOR_VERSION 10

#define PLUGIN_MICRO_VERSION 01

#define PLUGIN_VERSION \
    PLUGIN_VERSION_IMPLEMENTATION( \
        PLUGIN_MAJOR_VERSION, PLUGIN_MINOR_VERSION, PLUGIN_MICRO_VERSION)

#define PLUGIN_VERSION_IMPLEMENTATION(major, minor, micro) \
    PLUGIN_VERSION_TO_STRING(major) "-" \
    PLUGIN_VERSION_TO_STRING(minor) "-" \
    PLUGIN_VERSION_TO_STRING(micro)

#define PLUGIN_VERSION_TO_STRING(version) #version


#endif
