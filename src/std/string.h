#pragma once
#include <stdarg.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include "Error.h"


/**
 * Create a copy of a string.
 *
 * @param string input string
 * @param error error message, if any
 * @return new copy of the given string or `NULL` on error
 * @exception ENOMEM not enough memory
 */
char* strcopy(const char* string, Error* error);


/**
 * Format a string as `sprintf`, but safer.
 *
 * @param format format string
 * @param error error message, if any
 * @param ... format arguments
 * @return new formatted string or `NULL` on error
 * @exception ENOMEM not enough memory
 */
char* strformat(const char* format, Error* error, ...);


/**
 * Concatenate an array of strings.
 *
 * @param length how many strings to concatenate
 * @param strings array of strings to concatenate
 * @param separator string to use as the separator
 * @param error error message, if any
 * @return new joined string or `NULL` on error
 * @exception ENOMEM not enough memory
 */
char* strjoin(
    size_t length, const char** strings, const char* separator, Error* error);


/**
 * Create a partial copy of a string.
 *
 * @param string input string
 * @param length maximum number of characters to copy
 * @param error error message, if any
 * @return new partial copy of the given string or `NULL` on error
 * @exception ENOMEM not enough memory
 */
char* strncopy(const char* string, size_t length, Error* error);


/**
 * Check if a string has a prefix.
 *
 * @param string string to check
 * @param prefix prefix to check for
 * @return `true` if the string has the given prefix or `false` otherwise
 */
bool strprefix(const char* string, const char* prefix);


/**
 * Split a string into tokens.
 *
 * A token is a non-empty string not occurring in the separator.
 *
 * @param string string to split
 * @param separator string to use as the separator
 * @param length where to store the number of tokens found
 * @param error error message, if any
 * @return `NULL` terminated array of tokens or `NULL` on error
 * @exception ENOMEM not enough memory
 */
char** strsplit(
    const char* string, const char* separator, size_t* length, Error* error);


/**
 * Check if a string has a suffix.
 *
 * @param string string to check
 * @param suffix suffix to check for
 * @return `true` if the string has the given suffix or `false` otherwise
 */
bool strsuffix(const char* string, const char* suffix);


/**
 * Format a string as `vsprintf`, but safer.
 *
 * @param format format string
 * @param arguments format arguments list
 * @param error error message, if any
 * @return new formatted string or `NULL` on error
 * @exception ENOMEM not enough memory
 */
char* strvformat(const char* format, va_list arguments, Error* error);
