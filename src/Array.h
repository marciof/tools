#pragma once
#include <stddef.h>
#include <stdint.h>
#include "Error.h"

#define ARRAY_INITIAL_CAPACITY ((size_t) 8)
#define ARRAY_NULL_INITIALIZER {NULL, {0}, 0, 0}

#define /* bool */ ARRAY_IS_NULL_INITIALIZED(/* Array* */ array) \
    ((array)->data == NULL)

#define /* size_t */ C_ARRAY_LENGTH(array /* [] */) \
    (sizeof(array) / sizeof((array)[0]))

struct Array {
    intptr_t* data;
    intptr_t buffer[ARRAY_INITIAL_CAPACITY];
    size_t length;
    size_t capacity;
};

// Argument list must end with a `NULL`.
void Array_init(struct Array* array, Error* error, ...);

void Array_add(struct Array* array, size_t pos, intptr_t item, Error* error);
void Array_deinit(struct Array* array);
void Array_extend(struct Array* array, struct Array* items, Error* error);
intptr_t Array_remove(struct Array* array, size_t pos, Error* error);
