#ifndef __NPMESSAGING__
#define __NPMESSAGING__


#define PLUGIN_NAME "Messaging"

#define PLUGIN_DESCRIPTION "Instant messaging plug-in for Opera."

#define PLUGIN_MIME_TYPE "application/x-im"

#define PLUGIN_MAJOR_VERSION 2009

#define PLUGIN_MINOR_VERSION 02

#define PLUGIN_MICRO_VERSION 28

#define PLUGIN_VERSION \
    PLUGIN_VERSION_IMPLEMENTATION(PLUGIN_MAJOR_VERSION, PLUGIN_MINOR_VERSION, PLUGIN_MICRO_VERSION)

#define PLUGIN_VERSION_IMPLEMENTATION(major, minor, micro) \
    PLUGIN_VERSION_TO_STRING(major) "-" PLUGIN_VERSION_TO_STRING(minor) "-" PLUGIN_VERSION_TO_STRING(micro)

#define PLUGIN_VERSION_TO_STRING(version) #version


#endif
