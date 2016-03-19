#ifndef __EON__LIBRARY__STD__STDIO__
#define __EON__LIBRARY__STD__STDIO__


/**
 * @file
 * @brief "stdio" header extensions
 *
 * Extends the standard "stdio" header file and provides missing definitions.
 */


#include <stdio.h>
#include "../util.h"


/**
 * Standard null stream, or @c NULL if unavailable.
 *
 * Discards everything written to and yields end of file when read from.
 *
 * @hideinitializer
 */
#define stdnull (*__stdnull_location())


PUBLIC FILE** __stdnull_location(void);


#endif
