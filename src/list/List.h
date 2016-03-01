#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "../iterator/Iterator.h"
#include "../std/Error.h"


typedef struct _List* List;

typedef struct _List_Impl {
    Iterator_Impl iterator;
    void* (*create)(Error* error);
    void (*destroy)(void* list, Error* error);
    intptr_t (*get)(void* list, size_t position, Error* error);
    intptr_t (*get_property)(void* list, size_t property, Error* error);
    void (*insert)(void* list, intptr_t element, size_t position, Error* error);
    size_t (*length)(void* list);
    intptr_t (*remove)(void* list, size_t position, Error* error);
    intptr_t (*replace)(
        void* list, intptr_t element, size_t position, Error* error);
    void (*reverse)(void* list, Error* error);
    void (*set_property)(
        void* list, size_t property, intptr_t value, Error* error);
    void (*sort)(void* list, int (* compare)(intptr_t, intptr_t), Error* error);
}* List_Impl;


/**
 * Add an element to a list.
 *
 * @param list list into which to add the element
 * @param element element to insert at the end of the list
 * @param error error message, if any
 * @exception ENOMEM not enough memory
 * @exception EPERM list is being iterated
 * @exception EPERM maximum number of elements (`SIZE_MAX`) reached
 */
void List_add(List list, intptr_t element, Error* error);


/**
 * Remove all elements from a list.
 *
 * @param list list to clear of all elements
 * @param error error message, if any
 * @exception EPERM list is being iterated
 */
void List_clear(List list, Error* error);


/**
 * Create a list.
 *
 * @param implementation list implementation to use
 * @param error error message, if any
 * @return new empty list or `NULL` on error
 * @exception ENOMEM not enough memory
 */
List List_create(List_Impl implementation, Error* error);


/**
 * Delete a list.
 *
 * @param list list to delete, unless `NULL`
 * @param error error message, if any
 * @exception EPERM list is being iterated
 */
void List_delete(List list, Error* error);


/**
 * Appends elements to a list.
 *
 * @param list list into which to add the elemente
 * @param elements list of elements to insert at the end
 * @param error error message, if any
 * @exception ENOMEM not enough memory
 * @exception EPERM list is being iterated
 * @exception EPERM maximum number of iterators (`SIZE_MAX`) reached
 * @exception EPERM maximum number of elements (`SIZE_MAX`) reached
 */
void List_extend(List list, List elements, Error* error);


/**
 * Get an element from a list.
 *
 * @param list list from which to retrieve an element
 * @param position index of the element to retrieve
 * @param error error message, if any
 * @return element at the given position or `NULL` on error
 * @exception EINVAL invalid position
 */
intptr_t List_get(List list, size_t position, Error* error);


/**
 * Query the value of a list property.
 *
 * @param list list for which to query a property
 * @param property property to query
 * @param error error message, if any
 * @return property's value or `NULL` on error
 * @exception EINVAL unknown property
 */
intptr_t List_get_property(List list, size_t property, Error* error);


/**
 * Insert an element into a list.
 *
 * @param list list into which to insert the element
 * @param element element to insert
 * @param position index where to insert the element
 * @param error error message, if any
 * @exception EINVAL invalid position
 * @exception ENOMEM not enough memory
 * @exception EPERM list is being iterated
 * @exception EPERM maximum number of elements (`SIZE_MAX`) reached
 */
void List_insert(List list, intptr_t element, size_t position, Error* error);


/**
 * Create an iterator for a list.
 *
 * @param list list for which to create an iterator
 * @param error error message, if any
 * @return new iterator for the given list or `NULL` on error
 * @exception ENOMEM not enough memory
 * @exception EPERM maximum number of iterators (`SIZE_MAX`) reached
 */
Iterator List_iterator(List list, Error* error);


/**
 * Get the length of a list.
 *
 * @param list list for which to get the number of elements
 * @return number of elements in the list
 */
size_t List_length(List list);


/**
 * Create a list, using the most appropriate implementation, from variable
 * arguments.
 *
 * @param error error message, if any
 * @param ... elements to add, until the first `NULL` argument
 * @return new empty list or `NULL` on error
 * @exception ENOMEM not enough memory
 * @exception EPERM maximum number of elements (`SIZE_MAX`) reached
 */
List List_new(Error* error, ...);


/**
 * Remove an element from a list.
 *
 * @param list list from which to remove an element
 * @param position index of the element to remove
 * @param error error message, if any
 * @return removed element or `NULL` on error
 * @exception EINVAL invalid position
 * @exception EPERM list is being iterated
 */
intptr_t List_remove(List list, size_t position, Error* error);


/**
 * Replace an element with another in a list.
 *
 * @param list list in which to replace an element
 * @param element element to use as the replacement
 * @param position index of the element to replace
 * @param error error message, if any
 * @return replaced element or `NULL` on error
 * @exception EINVAL invalid position
 */
intptr_t List_replace(
    List list, intptr_t element, size_t position, Error* error);


/**
 * Reverse a list.
 *
 * @param list list for which to reverse the order of its elements
 * @param error error message, if any
 * @exception EPERM list is being iterated
 */
void List_reverse(List list, Error* error);


/**
 * Define the value of a list property.
 *
 * @param list list for which to define a property
 * @param property property to define
 * @param value property's value
 * @param error error message, if any
 * @return `true` if the property was correctly set or `false` otherwise
 * @exception EINVAL unknown property or invalid value
 */
bool List_set_property(
    List list, size_t property, intptr_t value, Error* error);


/**
 * Sort a list.
 *
 * @param list list to sort
 * @param compare comparison function that returns a negative number, zero,
 *        or a positive number if the first argument is considered to be
 *        respectively less than, equal to, greater than the second (if `NULL`
 *        uses the subtraction operator on each element)
 * @param error error message, if any
 * @exception EPERM list is being iterated
 */
void List_sort(List list, int (*compare)(intptr_t, intptr_t), Error* error);


/**
 * Convert a list to an array.
 *
 * @param list list to convert
 * @param data_size size of each element in bytes
 * @param error error message, if any
 * @return new array with all elements or `NULL` on error
 * @exception EINVAL empty list
 * @exception EINVAL zero data size
 * @exception ENOMEM not enough memory
 */
void* List_to_array(List list, size_t data_size, Error* error);
