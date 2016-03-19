#ifndef __EON__LIBRARY__MAP__MAP_IMPLEMENTATION__
#define __EON__LIBRARY__MAP__MAP_IMPLEMENTATION__


/**
 * @file
 * @brief Map implementation interface
 *
 * Defines a generic interface for map implementations.
 */


#include "../iterator/Iterator_Implementation.h"
#include "../ptr.h"
#include "../std/errno.h"
#include "../std/limits.h"
#include "../types.h"


/**
 * Map implementation interface.
 *
 * @see #Map
 */
typedef struct _Map_Implementation* Map_Implementation;

struct _Map_Implementation {
    Iterator_Implementation keys_iterator;
    void* (*create)(int* error);
    void (*destroy)(int* error, void* map);
    ptr_t (*get)(int* error, void* map, ptr_t key);
    ptr_t (*get_property)(int* error, void* map, size_t property);
    ptr_t (*put)(int* error, void* map, ptr_t key, ptr_t value);
    ptr_t (*remove)(int* error, void* map, ptr_t key);
    void (*set_property)(int* error, void* map, size_t property, ptr_t value);
    size_t (*size)(int* error, void* map);
};


#endif
