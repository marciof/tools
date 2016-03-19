#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "../Error.h"


typedef struct _Iterator* Iterator;

typedef struct _Iterator_Impl {
    void* (*create)(void* collection, Error* error);
    void (*destroy)(void* iterator);
    void (*to_end)(void* iterator);
    void (*to_start)(void* iterator);
    bool (*has_next)(void* iterator);
    bool (*has_previous)(void* iterator);
    intptr_t (*next)(void* iterator, Error* error);
    intptr_t (*previous)(void* iterator, Error* error);
}* Iterator_Impl;


/**
 * Delete an iterator.
 *
 * @param iterator iterator to delete, unless `NULL`
 */
void Iterator_delete(Iterator iterator);


/**
 * Check if an iterator has more elements when going forward.
 *
 * @param iterator iterator to check
 * @return `true` if the iterator has more elements or `false` otherwise
 */
bool Iterator_has_next(Iterator iterator);


/**
 * Check if an iterator has more elements when going backward.
 *
 * @param iterator iterator to check
 * @return `true` if the iterator has more elements or `false` otherwise
 */
bool Iterator_has_previous(Iterator iterator);


/**
 * Create an iterator.
 *
 * @param impl iterator implementation
 * @param collection collection to create an iterator for
 * @param error error message, if any
 * @return new iterator for the given collection or `NULL` on error
 * @exception ENOMEM not enough memory
 * @exception EPERM maximum number `SIZE_MAX` of iterators reached
 */
Iterator Iterator_new(Iterator_Impl impl, void* collection, Error* error);


/**
 * Get the next element from an iterator and move it forward.
 *
 * @param iterator iterator to retrieve the next element from
 * @param error error message, if any
 * @return next element or `NULL` on error
 * @exception EPERM no more next elements
 */
intptr_t Iterator_next(Iterator iterator, Error* error);


/**
 * Get the previous element from an iterator and move it backward.
 *
 * @param iterator iterator to retrieve the previous element from
 * @param error error message, if any
 * @return previous element or `NULL` on error
 * @exception EPERM no more previous elements
 */
intptr_t Iterator_previous(Iterator iterator, Error* error);


/**
 * Move an iterator to the end.
 *
 * @param iterator iterator to move to the end of its collection
 */
void Iterator_to_end(Iterator iterator);


/**
 * Move an iterator to the start.
 *
 * @param iterator iterator to move to the start of its collection
 */
void Iterator_to_start(Iterator iterator);
