#include <errno.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include "Array_List.h"
#include "List.h"


struct _List {
    List_Impl impl;
    void* list;
};


/**
 * Default comparison function for sorting a list.
 *
 * @param a first element
 * @param b second element
 * @return negative number, zero, or a positive number if the first element
 *         is considered to be respectively less than, equal to, or greater
 *         than the second
 */
static int default_comparison(intptr_t a, intptr_t b) {
    if (a < b) {
        return -1;
    }
    else if (a > b) {
        return 1;
    }
    else {
        return 0;
    }
}


void List_add(List list, intptr_t element, Error* error) {
    List_insert(list, element, List_length(list), error);
}


void List_clear(List list, Error* error) {
    for (size_t length = List_length(list); length > 0; --length) {
        List_remove(list, length - 1, error);
    }
}


List List_create(List_Impl implementation, Error* error) {
    List list = (List) malloc(sizeof(struct _List));

    if (list == NULL) {
        Error_errno(error, ENOMEM);
        return NULL;
    }

    list->impl = implementation;
    list->list = implementation->create(error);

    if (Error_has(error)) {
        free(list);
        return NULL;
    }

    Error_clear(error);
    return list;
}


void List_delete(List list, Error* error) {
    if (list != NULL) {
        list->impl->destroy(list->list, error);
        
        if (Error_has(error)) {
            return;
        }

        memset(list, 0, sizeof(struct _List));
        free(list);
    }

    Error_clear(error);
}


void List_extend(List list, List elements, Error* error) {
    size_t length = List_length(list);
    size_t nr_to_add = List_length(elements);
    size_t nr_added = 0;

    for (size_t i = 0; i < nr_to_add; ++i, ++nr_added) {
        intptr_t element = List_get(elements, i, error);

        if (Error_has(error)) {
            goto ERROR;
        }

        List_add(list, element, error);

        if (Error_has(error)) {
            goto ERROR;
        }

        continue;

        ERROR:
        for (; nr_added > 0; --nr_added) {
            List_remove(list, length + nr_added - 1, NULL);
        }
        return;
    }

    Error_clear(error);
}


intptr_t List_get(List list, size_t position, Error* error) {
    return list->impl->get(list->list, position, error);
}


intptr_t List_get_property(List list, size_t prop, Error* error) {
    return list->impl->get_property(list->list, prop, error);
}


void List_insert(List list, intptr_t element, size_t position, Error* error) {
    list->impl->insert(list->list, element, position, error);
}


size_t List_length(List list) {
    return list->impl->length(list->list);
}


List List_new(Error* error, ...) {
    List list = List_create(Array_List, error);

    if (Error_has(error)) {
        return NULL;
    }

    va_list args;
    va_start(args, error);

    for (intptr_t arg; (arg = va_arg(args, intptr_t)) != (intptr_t) NULL;) {
        List_add(list, arg, error);

        if (Error_has(error)) {
            va_end(args);
            List_delete(list, NULL);
            return NULL;
        }
    }

    va_end(args);
    Error_clear(error);
    return list;
}


intptr_t List_remove(List list, size_t position, Error* error) {
    return list->impl->remove(list->list, position, error);
}


intptr_t List_replace(
        List list, intptr_t element, size_t position, Error* error) {

    return list->impl->replace(list->list, element, position, error);
}


void List_reverse(List list, Error* error) {
    list->impl->reverse(list->list, error);
}


bool List_set_property(
        List list, size_t property, intptr_t value, Error* error) {

    list->impl->set_property(list->list, property, value, error);
    return !*error;
}


void List_sort(List list, int (*compare)(intptr_t, intptr_t), Error* error) {
    if (compare == NULL) {
        compare = default_comparison;
    }

    list->impl->sort(list->list, compare, error);
}


void* List_to_array(List list, size_t data_size, Error* error) {
    size_t length = List_length(list);

    if (length == 0) {
        Error_errno(error, EINVAL);
        return NULL;
    }
    
    if (data_size == 0) {
        Error_errno(error, EINVAL);
        return NULL;
    }
    
    void* array = malloc(data_size * List_length(list));
    
    if (array == NULL) {
        Error_errno(error, ENOMEM);
        return NULL;
    }
    
    uint8_t* location = (uint8_t*) array;

    for (size_t i = 0; i < length; ++i) {
        intptr_t element = List_get(list, i, error);

        if (Error_has(error)) {
            free(array);
            return NULL;
        }

        memcpy(location, &element, data_size);
        location += data_size;
    }
    
    Error_clear(error);
    return array;
}
