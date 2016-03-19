#include "../std/stdlib.h"
#include "../std/string.h"
#include "Iterator.h"


struct _Iterator {
    Iterator_Implementation implementation;
    void* iterator;
};


void Iterator_delete(Iterator iterator) {
    if (iterator != NULL) {
        int error;
        
        iterator->implementation->destroy(&error, iterator->iterator);
        memset(iterator, 0, sizeof(struct _Iterator));
        free(iterator);
    }
    
    errno = ENONE;
}


bool Iterator_has_next(Iterator iterator) {
    int error;
    
    errno = ENONE;
    return iterator->implementation->has_next(&error, iterator->iterator);
}


bool Iterator_has_previous(Iterator iterator) {
    int error;
    
    errno = ENONE;
    return iterator->implementation->has_previous(&error, iterator->iterator);
}


Iterator Iterator_new(Iterator_Implementation impl, void* collection) {
    Iterator iterator = (Iterator) malloc(sizeof(struct _Iterator));
    int error;
    
    if (iterator == NULL) {
        errno = ENOMEM;
        return NULL;
    }
    
    iterator->implementation = impl;
    iterator->iterator = impl->create(&error, collection);
    
    if (error != ENONE) {
        free(iterator);
        errno = error;
        return NULL;
    }
    
    errno = ENONE;
    return iterator;
}


ptr_t Iterator_next(Iterator iterator) {
    int error;
    ptr_t element = iterator->implementation->next(&error, iterator->iterator);
    
    errno = error;
    return element;
}


ptr_t Iterator_previous(Iterator iterator) {
    int error;
    ptr_t elem = iterator->implementation->previous(&error, iterator->iterator);
    
    errno = error;
    return elem;
}


void Iterator_to_end(Iterator iterator) {
    int error;
    
    iterator->implementation->to_end(&error, iterator->iterator);
    errno = ENONE;
}


void Iterator_to_start(Iterator iterator) {
    int error;
    
    iterator->implementation->to_start(&error, iterator->iterator);
    errno = ENONE;
}
