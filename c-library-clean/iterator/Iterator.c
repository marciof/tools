#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include "Iterator.h"


struct _Iterator {
    Iterator_Impl impl;
    void* iterator;
};


void Iterator_delete(Iterator iterator) {
    if (iterator != NULL) {
        iterator->impl->destroy(iterator->iterator);
        memset(iterator, 0, sizeof(struct _Iterator));
        free(iterator);
    }
}


bool Iterator_has_next(Iterator iterator) {
    return iterator->impl->has_next(iterator->iterator);
}


bool Iterator_has_previous(Iterator iterator) {
    return iterator->impl->has_previous(iterator->iterator);
}


Iterator Iterator_new(Iterator_Impl impl, void* collection, Error* error) {
    Iterator iterator = (Iterator) malloc(sizeof(struct _Iterator));

    if (iterator == NULL) {
        Error_errno(error, ENOMEM);
        return NULL;
    }
    
    iterator->impl = impl;
    iterator->iterator = impl->create(collection, error);
    
    if (Error_has(error)) {
        free(iterator);
        return NULL;
    }
    
    Error_clear(error);
    return iterator;
}


intptr_t Iterator_next(Iterator iterator, Error* error) {
    return iterator->impl->next(iterator->iterator, error);
}


intptr_t Iterator_previous(Iterator iterator, Error* error) {
    return iterator->impl->previous(iterator->iterator, error);
}


void Iterator_to_end(Iterator iterator) {
    iterator->impl->to_end(iterator->iterator);
}


void Iterator_to_start(Iterator iterator) {
    iterator->impl->to_start(iterator->iterator);
}
