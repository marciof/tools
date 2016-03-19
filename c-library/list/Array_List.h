#ifndef __EON__LIBRARY__LIST__ARRAY_LIST__
#define __EON__LIBRARY__LIST__ARRAY_LIST__


/**
 * @file
 * @brief Array list implementation
 *
 * Contains an array list implementation using a list interface.
 */


#include "../types.h"
#include "../util.h"
#include "List_Implementation.h"


/**
 * Valid properties for an array list.
 *
 * @see #List_get_property
 * @see #List_set_property
 */
enum {
    /**
     * Maximum number of elements the array can hold before actually resizing.
     * Must be greater than or equal to the array length.
     *
     * @note @b Type: @c size_t
     * @note @b Access: read/write
     * @note Errors that set @c errno to:
     *       - @c ENOMEM: Not enough memory.
     *       - @c EINVAL: Invalid capacity.
     */
    ARRAY_LIST_CAPACITY
};


/**
 * Array list implementation.
 *
 * The sorting algorithm is stable and is O(n log n) in time and O(1) in memory.
 *
 * @see #List_new
 */
PUBLIC const List_Implementation Array_List;


#endif
