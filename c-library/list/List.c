#include "../std/stdlib.h"
#include "../std/string.h"
#include "List.h"


struct _List {
    List_Implementation implementation;
    void* list;
};


/**
 * Default comparison function for sorting a list.
 *
 * @param [in] x first element
 * @param [in] y second element
 * @return negative number, zero, or a positive number if the first element
 *         is considered to be respectively less than, equal to, or greater
 *         than the second
 */
static int default_comparison(ptr_t x, ptr_t y) {
    if (x.data < y.data) {
        return -1;
    }
    else if (x.data > y.data) {
        return 1;
    }
    else {
        return 0;
    }
}


void List_add(List list, ptr_t element) {
    List_insert(list, element, List_length(list));
}


void List_delete(List list) {
    if (list != NULL) {
        int error;
        list->implementation->destroy(&error, list->list);
        
        if (error != ENONE) {
            errno = error;
            return;
        }
        
        memset(list, 0, sizeof(struct _List));
        free(list);
    }
    
    errno = ENONE;
}


ptr_t List_get(List list, size_t position) {
    int error;
    ptr_t element = list->implementation->get(&error, list->list, position);
    
    errno = error;
    return element;
}


ptr_t List_get_property(List list, size_t prop) {
    int error;
    ptr_t value = list->implementation->get_property(&error, list->list, prop);
    
    errno = error;
    return value;
}


void List_insert(List list, ptr_t element, size_t position) {
    int error;
    
    list->implementation->insert(&error, list->list, element, position);
    errno = error;
}


Iterator List_iterator(List list) {
    return Iterator_new(list->implementation->iterator, list->list);
}


size_t List_length(List list) {
    int error;
    
    errno = ENONE;
    return list->implementation->length(&error, list->list);
}


List List_new(List_Implementation implementation) {
    List list = (List) malloc(sizeof(struct _List));
    int error;
    
    if (list == NULL) {
        errno = ENOMEM;
        return NULL;
    }
    
    list->implementation = implementation;
    list->list = implementation->create(&error);
    
    if (error != ENONE) {
        free(list);
        errno = error;
        return NULL;
    }
    
    errno = ENONE;
    return list;
}


ptr_t List_remove(List list, size_t position) {
    int error;
    ptr_t element = list->implementation->remove(&error, list->list, position);
    
    errno = error;
    return element;
}


ptr_t List_replace(List list, ptr_t element, size_t position) {
    int error;
    ptr_t previous = list->implementation->replace(&error, list->list,
        element, position);
    
    errno = error;
    return previous;
}


void List_reverse(List list) {
    int error;
    
    list->implementation->reverse(&error, list->list);
    errno = error;
}


bool List_set_property(List list, size_t property, ptr_t value) {
    int error;
    
    list->implementation->set_property(&error, list->list, property, value);
    errno = error;
    
    return error == ENONE;
}


void List_sort(List list, int (*compare)(ptr_t, ptr_t)) {
    int error;
    
    if (compare == NULL) {
        compare = default_comparison;
    }
    
    list->implementation->sort(&error, list->list, compare);
    errno = error;
}


void* List_to_array(List list, size_t data_size) {
    Iterator it;
    void* array;
    uint8_t* location;
    bool is_data = true;
    size_t i;
    
    if (List_length(list) == 0) {
        errno = EINVAL;
        return NULL;
    }
    
    if (data_size == 0) {
        is_data = false;
        data_size = sizeof(void (*)());
    }
    
    array = malloc(data_size * List_length(list));
    
    if (array == NULL) {
        errno = ENOMEM;
        return NULL;
    }
    
    it = List_iterator(list);
    location = (uint8_t*) array;
    
    for (i = 0; i < List_length(list); ++i, location += data_size) {
        ptr_t element = (it == NULL) ? List_get(list, i) : Iterator_next(it);
        void* source = is_data ? (void*) &element.data : (void*) &element.code;
        
        memcpy(location, source, data_size);
    }
    
    Iterator_delete(it);
    errno = ENONE;
    return array;
}
