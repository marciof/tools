#include <errno.h>
#include <stdlib.h>
#include <string.h>
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


void List_delete(List list, Error* error) {
    if (list != NULL) {
        list->impl->destroy(list->list, error);
        
        if (*error) {
            return;
        }
        
        free(list);
    }
    
    *error = NULL;
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


Iterator List_iterator(List list, Error* error) {
    return Iterator_new(list->impl->iterator, list->list, error);
}


size_t List_length(List list) {
    return list->impl->length(list->list);
}


List List_new(List_Impl implementation, Error* error) {
    List list = (List) malloc(sizeof(struct _List));

    if (list == NULL) {
        *error = strerror(ENOMEM);
        return NULL;
    }
    
    list->impl = implementation;
    list->list = implementation->create(error);
    
    if (*error) {
        free(list);
        return NULL;
    }
    
    *error = NULL;
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
    if (List_length(list) == 0) {
        *error = strerror(EINVAL);
        return NULL;
    }
    
    if (data_size == 0) {
        *error = strerror(EINVAL);
        return NULL;
    }
    
    void* array = malloc(data_size * List_length(list));
    
    if (array == NULL) {
        *error = strerror(ENOMEM);
        return NULL;
    }
    
    Iterator it = List_iterator(list, error);
    uint8_t* location = (uint8_t*) array;

    while (Iterator_has_next(it)) {
        intptr_t element = Iterator_next(it, error);

        if (*error) {
            Iterator_delete(it);
            free(array);
            return NULL;
        }

        memcpy(location, &element, data_size);
        location += data_size;
    }
    
    Iterator_delete(it);
    *error = NULL;
    return array;
}
