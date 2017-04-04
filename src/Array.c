#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include "Array.h"

#define DEFAULT_CAPACITY_INCREASE (1.5)

static void change_capacity(struct Array* array, size_t size, Error* error) {
    if (size < array->length) {
        ERROR_ADD_STRING(error, "array capacity is smaller than its length");
        return;
    }

    if ((size > ARRAY_INITIAL_CAPACITY) && (array->data == array->buffer)) {
        array->data = (intptr_t*) malloc(size * sizeof(array->data[0]));

        if (array->data == NULL) {
            ERROR_ADD_ERRNO(error, errno);
            array->data = array->buffer;
            return;
        }

        memcpy(array->data, array->buffer,
            ARRAY_INITIAL_CAPACITY * sizeof(array->data[0]));
    }
    else {
        void* data = realloc(array->data, size * sizeof(array->data[0]));

        if (data == NULL) {
            ERROR_ADD_ERRNO(error, errno);
            return;
        }

        array->data = (intptr_t*) data;
    }

    array->capacity = size;
}

void Array_add(struct Array* array, size_t pos, intptr_t item, Error* error) {
    if (pos > array->length) {
        ERROR_ADD_STRING(error, "out of bounds array position for adding");
        return;
    }

    if (array->length == SIZE_MAX) {
        ERROR_ADD_ERRNO(error, ENOMEM);
        return;
    }

    if (array->length >= array->capacity) {
        size_t capacity = (size_t)
            (array->capacity * DEFAULT_CAPACITY_INCREASE + 1);

        if (capacity < (array->length + 1)) {
            capacity = SIZE_MAX; // cap overflow
        }

        change_capacity(array, capacity, error);

        if (ERROR_HAS(error)) {
            return;
        }
    }

    if (pos < array->length) {
        for (size_t i = array->length; i > pos; --i) {
            array->data[i] = array->data[i - 1];
        }
    }

    ++array->length;
    array->data[pos] = item;
}

void Array_deinit(struct Array* array) {
    if (array->data != array->buffer) {
        free(array->data);
        array->data = NULL;
    }
}

void Array_extend(struct Array* array, struct Array* items, Error* error) {
    if (items->length == 0) {
        return;
    }

    if (array->length > (SIZE_MAX - items->length)) {
        ERROR_ADD_ERRNO(error, ENOMEM);
        return;
    }

    if ((array->length + items->length) >= array->capacity) {
        size_t capacity = (size_t)
            (array->capacity * DEFAULT_CAPACITY_INCREASE + items->length);

        if (capacity < (array->length + items->length)) {
            capacity = SIZE_MAX; // cap overflow
        }

        change_capacity(array, capacity, error);

        if (ERROR_HAS(error)) {
            return;
        }
    }

    for (size_t i = 0; i < items->length; ++i, ++array->length) {
        array->data[array->length] = items->data[i];
    }
}

void Array_init(struct Array* array, Error* error, ...) {
    array->length = 0;
    array->capacity = ARRAY_INITIAL_CAPACITY;
    array->data = array->buffer;

    va_list args;
    va_start(args, error);

    for (intptr_t arg; (arg = va_arg(args, intptr_t)) != (intptr_t) NULL;) {
        Array_add(array, array->length, arg, error);

        if (ERROR_HAS(error)) {
            va_end(args);
            Array_deinit(array);
            return;
        }
    }

    va_end(args);
}

intptr_t Array_remove(struct Array* array, size_t pos, Error* error) {
    if (pos >= array->length) {
        ERROR_ADD_STRING(error, "out of bounds array position for removal");
        return 0;
    }

    --array->length;
    intptr_t element = array->data[pos];

    if (pos < array->length) {
        for (size_t i = pos; i < array->length; ++i) {
            array->data[i] = array->data[i + 1];
        }
    }

    return element;
}
