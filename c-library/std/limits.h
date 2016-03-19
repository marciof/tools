#ifndef __EON__LIBRARY__STD__LIMITS__
#define __EON__LIBRARY__STD__LIMITS__


/**
 * @file
 * @brief "limits" header extensions
 *
 * Extends the standard "limits" header file and provides missing definitions.
 */


#include <limits.h>
#include "../types.h"


#ifndef SIZE_MAX
    /** Maximum value of size_t. */
#   define SIZE_MAX ((size_t) ~0)
#endif


#endif
