#ifndef __EON__LIBRARY__STD__STDARG__
#define __EON__LIBRARY__STD__STDARG__


/**
 * @file
 * @brief "stdarg" header extensions
 *
 * Extends the standard "stdarg" header file and provides missing definitions.
 */


#include <stdarg.h>


/**
 * Copies a @c va_list.
 *
 * @hideinitializer
 * @param [out] to where to store the copy
 * @param [in] from @c va_list from which to create a copy
 */
#ifndef va_copy
#   ifndef __va_copy
#       define va_copy(to, from) \
            ((void) ((to) = (from)))
#   else
#       define va_copy __va_copy
#   endif
#endif


#endif
