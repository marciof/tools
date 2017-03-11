#pragma once
#include <stddef.h>
#include <stdint.h>
#include "Error.h"

#define STATIC_ARRAY_LENGTH(array) \
    (sizeof(array) / sizeof((array)[0]))

#define ARRAY_INITIAL_CAPACITY ((size_t) 8)
#define ARRAY_NULL_INITIALIZER {NULL}

#define /* bool */ ARRAY_IS_NULL(/* Array* */ array) \
    ((array)->data == NULL)

typedef struct {
    intptr_t* data;
    intptr_t buffer[ARRAY_INITIAL_CAPACITY];
    size_t length;
    size_t capacity;
} Array;

void Array_add(Array* array, size_t pos, intptr_t element, Error* error);
void Array_deinit(Array* array);
void Array_extend(Array* array, Array* elements, Error* error);
void Array_init(Array* array, Error* error, ...);
intptr_t Array_remove(Array* array, size_t pos, Error* error);
