#include <errno.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include "Array.h"

#define DEFAULT_INITIAL_CAPACITY ((size_t) 8)
#define DEFAULT_CAPACITY_INCREASE_FACTOR (1.5)

static void change_capacity(Array* array, size_t capacity, Error* error) {
    if (capacity < array->length) {
        Error_errno(error, EINVAL);
        return;
    }
    
    intptr_t* data = (intptr_t*) realloc(
        array->data, capacity * sizeof(intptr_t));
    
    if (data == NULL) {
        Error_errno(error, errno);
        return;
    }
    
    array->data = data;
    array->capacity = capacity;

    Error_clear(error);
    return;
}

void Array_add(Array* array, intptr_t element, Error* error) {
    Array_insert(array, element, array->length, error);
}

void Array_delete(Array* array) {
    if (array != NULL) {
        free(array->data);
        memset(array, 0, sizeof(*array));
        free(array);
    }
}

void Array_extend(Array* list, Array* elements, Error* error) {
    if (elements->length == 0) {
        Error_clear(error);
        return;
    }

    change_capacity(list, list->length + elements->length, error);

    if (Error_has(error)) {
        return;
    }

    for (size_t i = 0; i < elements->length; ++i, ++list->length) {
        list->data[list->length] = elements->data[i];
    }

    Error_clear(error);
}

void Array_insert(Array* array, intptr_t element, size_t position, Error* error) {
    if (position > array->length) {
        Error_errno(error, EINVAL);
        return;
    }

    if (array->length == SIZE_MAX) {
        Error_errno(error, EPERM);
        return;
    }

    if (array->length >= array->capacity) {
        change_capacity(
            array,
            (size_t) (array->capacity * DEFAULT_CAPACITY_INCREASE_FACTOR + 1),
            error);

        if (Error_has(error)) {
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
    Error_clear(error);
}

Array* Array_new(Error* error, ...) {
    Array* array = (Array*) malloc(sizeof(*array));

    if (array == NULL) {
        Error_errno(error, errno);
        return NULL;
    }

    array->length = 0;
    array->capacity = DEFAULT_INITIAL_CAPACITY;
    array->data = (intptr_t*) malloc(array->capacity * sizeof(intptr_t));

    if (array->data == NULL) {
        free(array);
        Error_errno(error, errno);
        return NULL;
    }

    va_list args;
    va_start(args, error);

    for (intptr_t arg; (arg = va_arg(args, intptr_t)) != (intptr_t) NULL; ) {
        Array_add(array, arg, error);

        if (Error_has(error)) {
            va_end(args);
            Array_delete(array);
            return NULL;
        }
    }

    va_end(args);
    Error_clear(error);
    return array;
}

intptr_t Array_remove(Array* array, size_t position, Error* error) {
    if (position >= array->length) {
        Error_errno(error, EINVAL);
        return 0;
    }

    --array->length;
    intptr_t element = array->data[position];

    if (position < array->length) {
        for (size_t i = position; i < array->length; ++i) {
            array->data[i] = array->data[i + 1];
        }
    }

    Error_clear(error);
    return element;
}
