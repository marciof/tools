#ifndef __EON__LIBRARY__ITERATOR__ITERATOR_IMPLEMENTATION__
#define __EON__LIBRARY__ITERATOR__ITERATOR_IMPLEMENTATION__


/**
 * @file
 * @brief Iterator implementation interface
 *
 * Defines a generic interface for iterator implementations.
 */


#include "../ptr.h"
#include "../std/errno.h"
#include "../std/limits.h"
#include "../types.h"


/**
 * Iterator implementation interface.
 *
 * @see #Iterator
 */
typedef struct _Iterator_Implementation* Iterator_Implementation;

struct _Iterator_Implementation {
    void* (*create)(int* error, void* collection);
    void (*destroy)(int* error, void* iterator);
    void (*to_end)(int* error, void* iterator);
    void (*to_start)(int* error, void* iterator);
    bool (*has_next)(int* error, void* iterator);
    bool (*has_previous)(int* error, void* iterator);
    ptr_t (*next)(int* error, void* iterator);
    ptr_t (*previous)(int* error, void* iterator);
};


#endif
