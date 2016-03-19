#ifndef __EON__LIBRARY__PTR__
#define __EON__LIBRARY__PTR__


/**
 * @file
 * @brief Generic pointer
 *
 * Defines a generic pointer data type.
 */


#include "util.h"


/**
 * Generic pointer capable of storing code and data pointers.
 *
 * @see #CODE
 * @see #DATA
 * @see #null
 */
typedef union {
    /** Code pointer. */
    void (*code)();
    
    /** Data pointer. */
    void* data;
}
ptr_t;


/**
 * Wraps a code (function) pointer.
 *
 * @code
 * ptr_t p = CODE(printf);
 * @endcode
 *
 * @hideinitializer
 * @param [in] code code pointer to wrap
 * @return given code pointer wrapped in a generic pointer
 * @see #ptr_t
 */
#define CODE(code) \
    __wrap_code_pointer((void (*)()) (code))


/**
 * Wraps a data (object) pointer.
 *
 * @code
 * int i = 123;
 * ptr_t p = DATA(&i);
 * @endcode
 *
 * @hideinitializer
 * @param [in] data data pointer to wrap
 * @return given data pointer wrapped in a generic pointer
 * @see #ptr_t
 */
#define DATA(data) \
    __wrap_data_pointer((void*) (data))


/**
 * Generic null pointer.
 */
PUBLIC const ptr_t null;


PUBLIC ptr_t __wrap_code_pointer(void (*code)());
PUBLIC ptr_t __wrap_data_pointer(void* data);


#endif
