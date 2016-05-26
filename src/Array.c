#include <errno.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include "Array.h"

#define DEFAULT_CAPACITY_INCREASE_FACTOR (1.5)

static void change_capacity(Array* array, size_t capacity, Error* error) {
    if (capacity < array->length) {
        ERROR_ERRNO(error, EINVAL);
        return;
    }

    if ((capacity > ARRAY_INITIAL_CAPACITY) && (array->data == array->buffer)) {
        array->data = (intptr_t*) malloc(capacity * sizeof(intptr_t));

        if (array->data == NULL) {
            ERROR_ERRNO(error, errno);
            array->data = array->buffer;
            return;
        }

        memcpy(array->data, array->buffer,
            ARRAY_INITIAL_CAPACITY * sizeof(intptr_t));
    }
    else {
        intptr_t* data = (intptr_t*) realloc(
            array->data, capacity * sizeof(intptr_t));

        if (data == NULL) {
            ERROR_ERRNO(error, errno);
            return;
        }

        array->data = data;
    }

    array->capacity = capacity;
    ERROR_CLEAR(error);
}

void Array_add(Array* array, size_t position, intptr_t element, Error* error) {
    if (position > array->length) {
        ERROR_ERRNO(error, EINVAL);
        return;
    }

    if (array->length == SIZE_MAX) {
        ERROR_ERRNO(error, EPERM);
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

    if (position < array->length) {
        for (size_t i = array->length; i > position; --i) {
            array->data[i] = array->data[i - 1];
        }
    }

    ++array->length;
    array->data[position] = element;
    ERROR_CLEAR(error);
}

void Array_deinit(Array* array) {
    if (array->data != array->buffer) {
        free(array->data);
    }
}

void Array_extend(Array* list, Array* elements, Error* error) {
    if (elements->length == 0) {
        ERROR_CLEAR(error);
        return;
    }

    for (size_t i = 0; i < elements->length; ++i, ++list->length) {
        list->data[list->length] = elements->data[i];
    }

    ERROR_CLEAR(error);
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
    ERROR_CLEAR(error);
}

intptr_t Array_remove(Array* array, size_t position, Error* error) {
    if (position >= array->length) {
        ERROR_ERRNO(error, EINVAL);
        return 0;
    }

    --array->length;
    intptr_t element = array->data[position];

    if (position < array->length) {
        for (size_t i = position; i < array->length; ++i) {
            array->data[i] = array->data[i + 1];
        }
    }

    ERROR_CLEAR(error);
    return element;
}
