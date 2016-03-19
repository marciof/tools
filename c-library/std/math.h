#ifndef __EON__LIBRARY__STD__MATH__
#define __EON__LIBRARY__STD__MATH__


/**
 * @file
 * @brief "math" header extensions
 *
 * Extends the standard "math" header file and provides missing definitions.
 */


#include <math.h>
#include "../types.h"


/**
 * @name Bit utilities
 * @{
 */

/**
 * Creates a bit.
 *
 * @param [in] position zero indexed position of the bit to create
 * @return new integer with the given bit set
 */
#define BIT(position) \
    (1 << (position))


/**
 * Clears a bit.
 *
 * @param [in] integer integer on which to clear a bit
 * @param [in] position zero indexed position of the bit to clear
 * @return new integer with the given bit cleared
 */
#define BIT_CLEAR(integer, position) \
    ((integer) & (~0 ^ BIT(position)))


/**
 * Gets a bit.
 *
 * @param [in] integer integer from which to retrieve a bit
 * @param [in] position zero indexed position of the bit to retrieve
 * @return new integer with only the given bit set
 */
#define BIT_GET(integer, position) \
    ((integer) & BIT(position))


/**
 * Checks if a bit is set.
 *
 * @param [in] integer integer to be checked for
 * @param [in] position zero indexed position of the bit to check for
 * @return @c true if the given bit is set or @c false otherwise
 */
#define BIT_IS_SET(integer, position) \
    (BIT_GET(integer, position) != 0 ? true : false)


/**
 * Sets a bit.
 *
 * @param [in] integer integer on which to set a bit
 * @param [in] position zero indexed position of the bit to set
 * @return new integer with the given bit set
 */
#define BIT_SET(integer, position) \
    ((integer) | BIT(position))

/* @} */


/**
 * Computes the greater of two values.
 *
 * @param [in] x first value
 * @param [in] y second value
 * @return maximum value
 * @attention The highest value will be evaluated twice.
 * @see #MIN
 */
#define MAX(x, y) \
    ((x) > (y) ? (x) : (y))


/**
 * Computes the smaller of two values.
 *
 * @param [in] x first value
 * @param [in] y second value
 * @return minimum value
 * @attention The lowest value will be evaluated twice.
 * @see #MAX
 */
#define MIN(x, y) \
    ((x) < (y) ? (x) : (y))


#endif
