#ifndef __EON__LIBRARY__STD__ERRNO__
#define __EON__LIBRARY__STD__ERRNO__


/**
 * @file
 * @brief "errno" header extensions
 *
 * Extends the standard "errno" header file and provides missing definitions.
 */


#include <errno.h>


/** No error. */
#define ENONE 0

#ifndef ENOTSUP
    /** Not supported error. */
#   define ENOTSUP 35
#endif


#endif
