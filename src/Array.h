#pragma once
#include <stddef.h>
#include <stdint.h>
#include "Error.h"

#define STATIC_ARRAY_LENGTH(array) \
    (sizeof(array) / sizeof((array)[0]))

typedef struct {
    intptr_t* data;
    size_t length;
    size_t capacity;
} Array;

void Array_add(Array* array, intptr_t element, size_t position, Error* error);
void Array_deinit(Array* array);
void Array_extend(Array* array, Array* elements, Error* error);
void Array_init(Array* array, Error* error, ...);
intptr_t Array_remove(Array* array, size_t position, Error* error);
