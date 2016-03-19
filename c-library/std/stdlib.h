#ifndef __EON__LIBRARY__STD__STDLIB__
#define __EON__LIBRARY__STD__STDLIB__


/**
 * @file
 * @brief "stdlib" header extensions
 *
 * Extends the standard "stdlib" header file and provides missing definitions.
 */


#include <stdlib.h>

#include "../ptr.h"
#include "../util.h"
#include "errno.h"


/**
 * Registers a function to be called on exit.
 *
 * Registered functions are called in the reverse order of their registration.
 *
 * @param [in] function function to register
 * @param [in] argument user defined value to use when calling the function
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC void atexit_ext(void (*function)(ptr_t argument), ptr_t argument);


#endif
