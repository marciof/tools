#ifndef __EON__LIBRARY__PROPERTIES__
#define __EON__LIBRARY__PROPERTIES__


/**
 * @file
 * @brief Library properties
 *
 * Allows users to manage miscellaneous information about this library.
 */


#include "ptr.h"
#include "std/errno.h"
#include "types.h"
#include "util.h"


/**
 * Full library version, as a long integer in the format @em YYYYMMDD.
 */
#define EON_LIBRARY_VERSION 20110205L


/**
 * Valid properties for this library.
 *
 * @see #Eon_Library_get_property
 * @see #Eon_Library_set_property
 */
enum {
    /**
     * The year this library's version was released.
     *
     * @note @b Type: @c size_t
     * @note @b Access: read
     */
    EON_LIBRARY_MAJOR_VERSION,
    
    /**
     * The month this library's version was released.
     *
     * @note @b Type: @c size_t
     * @note @b Access: read
     */
    EON_LIBRARY_MINOR_VERSION,
    
    /**
     * The day this library's version was released.
     *
     * @note @b Type: @c size_t
     * @note @b Access: read
     */
    EON_LIBRARY_MICRO_VERSION
};


/**
 * Queries the value of a library property.
 *
 * @param [in] property property to query
 * @return property's value or @c #null on error (see note)
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Unknown property.
 */
PUBLIC ptr_t Eon_Library_get_property(size_t property);


/**
 * Defines the value of a library property.
 *
 * @param [in] property property to define
 * @param [in] value property's value
 * @return @c true if the property was correctly set or @c false otherwise
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Unknown property or invalid value.
 */
PUBLIC bool Eon_Library_set_property(size_t property, ptr_t value);


#endif
