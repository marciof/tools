#ifndef __EON__LIBRARY__LIST__LIST_IMPLEMENTATION__
#define __EON__LIBRARY__LIST__LIST_IMPLEMENTATION__


/**
 * @file
 * @brief List implementation interface
 *
 * Defines a generic interface for list implementations.
 */


#include "../iterator/Iterator_Implementation.h"
#include "../ptr.h"
#include "../std/errno.h"
#include "../std/limits.h"
#include "../types.h"


/**
 * List implementation interface.
 *
 * @see #List
 */
typedef struct _List_Implementation* List_Implementation;

struct _List_Implementation {
    Iterator_Implementation iterator;
    void* (*create)(int* error);
    void (*destroy)(int* error, void* list);
    ptr_t (*get)(int* error, void* list, size_t position);
    ptr_t (*get_property)(int* error, void* list, size_t property);
    void (*insert)(int* error, void* list, ptr_t element, size_t position);
    size_t (*length)(int* error, void* list);
    ptr_t (*remove)(int* error, void* list, size_t position);
    ptr_t (*replace)(int* error, void* list, ptr_t element, size_t position);
    void (*reverse)(int* error, void* list);
    void (*set_property)(int* error, void* list, size_t property, ptr_t value);
    void (*sort)(int* error, void* list, int (*compare)(ptr_t, ptr_t));
};


#endif
