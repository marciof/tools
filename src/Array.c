#include <errno.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include "Array.h"

#define DEFAULT_CAPACITY_INCREASE (1.5)

static void change_capacity(Array* array, size_t size, Error* error) {
    if (size < array->length) {
        Error_add(error, "array capacity is smaller than its length");
        return;
    }

    if ((size > ARRAY_INITIAL_CAPACITY) && (array->data == array->buffer)) {
        array->data = (intptr_t*) malloc(size * sizeof(array->data[0]));

        if (array->data == NULL) {
            Error_add(error, strerror(errno));
            array->data = array->buffer;
            return;
        }

        memcpy(array->data, array->buffer,
            ARRAY_INITIAL_CAPACITY * sizeof(array->data[0]));
    }
    else {
        void* data = realloc(array->data, size * sizeof(array->data[0]));

        if (data == NULL) {
            Error_add(error, strerror(errno));
            return;
        }

        array->data = (intptr_t*) data;
    }

    array->capacity = size;
}

void Array_add(Array* array, size_t pos, intptr_t element, Error* error) {
    if (pos > array->length) {
        Error_add(error, "out of bounds array position for adding");
        return;
    }

    if (array->length == SIZE_MAX) {
        Error_add(error, strerror(ENOMEM));
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
    array->data[pos] = element;
}

void Array_deinit(Array* array) {
    if (array->data != array->buffer) {
        free(array->data);
        array->data = NULL;
    }
}

void Array_extend(Array* array, Array* elements, Error* error) {
    if (elements->length == 0) {
        return;
    }

    if (array->length > (SIZE_MAX - elements->length)) {
        Error_add(error, strerror(ENOMEM));
        return;
    }

    if ((array->length + elements->length) >= array->capacity) {
        size_t capacity = (size_t)
            (array->capacity * DEFAULT_CAPACITY_INCREASE + elements->length);

        if (capacity < (array->length + elements->length)) {
            capacity = SIZE_MAX; // cap overflow
        }

        change_capacity(array, capacity, error);

        if (ERROR_HAS(error)) {
            return;
        }
    }

    for (size_t i = 0; i < elements->length; ++i, ++array->length) {
        array->data[array->length] = elements->data[i];
    }
}

void Array_init(Array* array, Error* error, ...) {
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

intptr_t Array_remove(Array* array, size_t pos, Error* error) {
    if (pos >= array->length) {
        Error_add(error, "out of bounds array position for removal");
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
