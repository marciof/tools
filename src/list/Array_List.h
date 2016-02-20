#ifndef SHOW__LIST__ARRAY_LIST_H
#define SHOW__LIST__ARRAY_LIST_H


#include "List.h"


enum Array_List_Properties {
    /**
     * Maximum number of elements the array can hold before actually resizing.
     * Must be greater than or equal to the array length.
     *
     * @exception ENOMEM Not enough memory.
     * @exception EINVAL Invalid capacity.
     */
    ARRAY_LIST_CAPACITY
};


/**
 * Array list implementation.
 *
 * The sorting algorithm is stable and is O(n log n) in time and O(1) in memory.
 */
extern const List_Impl Array_List;


#endif
