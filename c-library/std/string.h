#ifndef __EON__LIBRARY__STD__STRING__
#define __EON__LIBRARY__STD__STRING__


/**
 * @file
 * @brief "string" header extensions
 *
 * Extends the standard "string" header file and provides missing definitions.
 */


#include <string.h>

#include "../types.h"
#include "../util.h"
#include "errno.h"
#include "stdarg.h"
#include "stdlib.h"


/**
 * Creates a copy of a string.
 *
 * @param [in] string string to copy
 * @return new copy of the given string or @c NULL on error (see note)
 * @see #strncopy
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC char* strcopy(const char* string);


/**
 * Formats a string (as @c sprintf but safer).
 *
 * @code
 * char* date = strformat("%04d-%02d-%02d", year, month, day);
 * ...
 * free(date);
 * @endcode
 *
 * @param [in] format format string
 * @param [in] ... format arguments
 * @return new formatted string or @c NULL on error (see note)
 * @see #strvformat
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC char* strformat(const char* format, ...);


/**
 * Concatenates an array of strings.
 *
 * @param [in] length how many strings to concatenate
 * @param [in] strings array of strings to concatenate
 * @param [in] separator string to use as the separator
 * @return new joined string or @c NULL on error (see note)
 * @see #strsplit
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC char* strjoin(size_t length, const char** strings, const char* separator);


/**
 * Creates a copy of part of a string.
 *
 * @param [in] string string to copy
 * @param [in] length maximum number of characters to copy
 * @return new partial copy of the given string or @c NULL on error (see note)
 * @see #strcopy
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC char* strncopy(const char* string, size_t length);


/**
 * Checks if a string has a prefix.
 *
 * @param [in] string string to check
 * @param [in] prefix prefix to check for
 * @return @c true if the string has the given prefix or @c false otherwise
 * @see #strsuffix
 */
PUBLIC bool strprefix(const char* string, const char* prefix);


/**
 * Splits a string into tokens.
 *
 * A token is a non-empty string not occurring in the separator.
 *
 * @code
 * char** components = strsplit("1986-01-07", "-", NULL);
 *
 * int year = atoi(components[0]);
 * int month = atoi(components[1]);
 * int day = atoi(components[2]);
 *
 * size_t i = 0;
 *
 * while (components[i] != NULL) {
 *     free(components[i++]);
 * }
 *
 * free(components);
 * @endcode
 *
 * @param [in] string string to split
 * @param [in] separator string to use as the separator
 * @param [out] length where to store the number of tokens found, unless @c NULL
 * @return @c NULL terminated array of tokens or @c NULL on error (see note)
 * @see #strjoin
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC char** strsplit(const char* string, const char* separator, size_t* length);


/**
 * Checks if a string has a suffix.
 *
 * @param [in] string string to check
 * @param [in] suffix suffix to check for
 * @return @c true if the string has the given suffix or @c false otherwise
 * @see #strprefix
 */
PUBLIC bool strsuffix(const char* string, const char* suffix);


/**
 * Formats a string (as @c vsprintf but safer).
 *
 * @param [in] format format string
 * @param [in] arguments format arguments list
 * @return new formatted string or @c NULL on error (see note)
 * @see #strformat
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC char* strvformat(const char* format, va_list arguments);


#endif
