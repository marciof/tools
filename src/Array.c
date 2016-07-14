#include <errno.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include "Array.h"

#define DEFAULT_CAPACITY_INCREASE_FACTOR (1.5)

static void change_capacity(Array* array, size_t size, Error* error) {
    if (size < array->length) {
        Error_add(error, "Array capacity is smaller than its length");
        return;
    }

    if ((size > ARRAY_INITIAL_CAPACITY) && (array->data == array->buffer)) {
        array->data = (intptr_t*) malloc(size * sizeof(intptr_t));

        if (array->data == NULL) {
            Error_add(error, strerror(errno));
            array->data = array->buffer;
            return;
        }

        memcpy(array->data, array->buffer,
            ARRAY_INITIAL_CAPACITY * sizeof(intptr_t));
    }
    else {
        void* data = realloc(array->data, size * sizeof(intptr_t));

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
        Error_add(error, "Out of bounds array position for adding");
        return;
    }

    if (array->length == SIZE_MAX) {
        Error_add(error, strerror(ENOMEM));
        return;
    }

    if (array->length >= array->capacity) {
        change_capacity(
            array,
            (size_t) (array->capacity * DEFAULT_CAPACITY_INCREASE_FACTOR + 1),
            error);

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
    }
}

void Array_extend(Array* list, Array* elements, Error* error) {
    if (elements->length > 0) {
        for (size_t i = 0; i < elements->length; ++i, ++list->length) {
            list->data[list->length] = elements->data[i];
        }
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
        Error_add(error, "Out of bounds array position for removal");
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
