#include "properties.h"
#include "std/string.h"
#include "util.h"


WARN_DEPRECATION_DISABLE


static size_t major_version = 0;
static size_t minor_version = 0;
static size_t micro_version = 0;


/**
 * Splits the library version into its components.
 */
static void parse_version() {
    const char* version = TO_STRING_INDIRECT(EON_LIBRARY_VERSION);
    char major[4 + 1] = {'\0'};
    char minor[2 + 1] = {'\0'};
    char micro[2 + 1] = {'\0'};
    
    strncpy(major, version, LENGTH_OF(major) - 1);
    version += LENGTH_OF(major) - 1;
    
    strncpy(minor, version, LENGTH_OF(minor) - 1);
    version += LENGTH_OF(minor) - 1;
    
    strncpy(micro, version, LENGTH_OF(micro) - 1);
    
    major_version = strtoul(major, NULL, 10);
    minor_version = strtoul(minor, NULL, 10);
    micro_version = strtoul(micro, NULL, 10);
}


ptr_t Eon_Library_get_property(size_t property) {
    switch (property) {
    case EON_LIBRARY_MAJOR_VERSION:
        if (major_version == 0) {
            parse_version();
        }
        errno = ENONE;
        return DATA(major_version);
    case EON_LIBRARY_MINOR_VERSION:
        if (minor_version == 0) {
            parse_version();
        }
        errno = ENONE;
        return DATA(minor_version);
    case EON_LIBRARY_MICRO_VERSION:
        if (micro_version == 0) {
            parse_version();
        }
        errno = ENONE;
        return DATA(micro_version);
    default:
        errno = EINVAL;
        return null;
    }
}


bool Eon_Library_set_property(UNUSED size_t property, UNUSED ptr_t value) {
    errno = EINVAL;
    return false;
}
