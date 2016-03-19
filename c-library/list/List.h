#ifndef __EON__LIBRARY__LIST__LIST__
#define __EON__LIBRARY__LIST__LIST__


/**
 * @file
 * @brief List interface
 *
 * Defines the interface to manipulate list instances.
 */


#include "../iterator/Iterator.h"
#include "../std/stdlib.h"
#include "../types.h"
#include "../util.h"
#include "List_Implementation.h"


/**
 * List instance.
 */
typedef struct _List* List;


/**
 * Adds an element to a list.
 *
 * @param [in,out] list list into which to add the element
 * @param [in] element element to insert at the end of the list
 * @see #List_insert
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 *       - @c EPERM: List is being iterated.
 *       - @c EPERM: Maximum number of elements (@c SIZE_MAX) reached.
 */
PUBLIC void List_add(List list, ptr_t element);


/**
 * Deletes a list.
 *
 * @param [in,out] list list to delete, unless @c NULL
 * @see #List_new
 * @note Errors that set @c errno to:
 *       - @c EPERM: List is being iterated.
 */
PUBLIC void List_delete(List list);


/**
 * Gets an element from a list.
 *
 * @param [in] list list from which to retrieve an element
 * @param [in] position index of the element to retrieve
 * @return element at the given position or @c #null on error (see note)
 * @see #List_replace
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Invalid position.
 */
PUBLIC ptr_t List_get(List list, size_t position);


/**
 * Queries the value of a list property.
 *
 * @param [in] list list for which to query a property
 * @param [in] property property to query
 * @return property's value or @c #null on error (see note)
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Unknown property.
 */
PUBLIC ptr_t List_get_property(List list, size_t property);


/**
 * Inserts an element into a list.
 *
 * @param [in,out] list list into which to insert the element
 * @param [in] element element to insert
 * @param [in] position index where to insert the element
 * @see #List_add
 * @see #List_remove
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Invalid position.
 *       - @c ENOMEM: Not enough memory.
 *       - @c EPERM: List is being iterated.
 *       - @c EPERM: Maximum number of elements (@c SIZE_MAX) reached.
 */
PUBLIC void List_insert(List list, ptr_t element, size_t position);


/**
 * Creates an iterator for a list.
 *
 * @code
 * Iterator i = List_iterator(l);
 * 
 * while (Iterator_has_next(i)) {
 *     ptr_t element = Iterator_next(i);
 *     ...
 * }
 * 
 * Iterator_delete(i);
 * @endcode
 *
 * @param [in] list list for which to create an iterator
 * @return new iterator for the given list or @c NULL on error (see note)
 * @see #Iterator_delete
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 *       - @c EPERM: Maximum number of iterators (@c SIZE_MAX) reached.
 */
PUBLIC Iterator List_iterator(List list);


/**
 * Gets the length of a list.
 *
 * @param [in] list list for which to count the number of elements
 * @return number of elements in the list
 */
PUBLIC size_t List_length(List list);


/**
 * Creates a list.
 *
 * @code
 * List l = List_new(Array_List);
 * ...
 * List_delete(l);
 * @endcode
 *
 * @param [in] implementation list implementation to use
 * @return new empty list or @c NULL on error (see note)
 * @see #List_delete
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC List List_new(List_Implementation implementation);


/**
 * Removes an element from a list.
 *
 * @param [in,out] list list from which to remove an element
 * @param [in] position index of the element to remove
 * @return removed element or @c #null on error (see note)
 * @see #List_insert
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Invalid position.
 *       - @c EPERM: List is being iterated.
 */
PUBLIC ptr_t List_remove(List list, size_t position);


/**
 * Replaces an element with another in a list.
 *
 * @param [in,out] list list in which to replace an element
 * @param [in] element element to use as the replacement
 * @param [in] position index of the element to replace
 * @return replaced element or @c #null on error (see note)
 * @see #List_get
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Invalid position.
 */
PUBLIC ptr_t List_replace(List list, ptr_t element, size_t position);


/**
 * Reverses a list.
 *
 * @param [in,out] list list for which to reverse the order of its elements
 * @see #List_sort
 * @note Errors that set @c errno to:
 *       - @c EPERM: List is being iterated.
 */
PUBLIC void List_reverse(List list);


/**
 * Defines the value of a list property.
 *
 * @param [in,out] list list for which to define a property
 * @param [in] property property to define
 * @param [in] value property's value
 * @return @c true if the property was correctly set or @c false otherwise
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Unknown property or invalid value.
 */
PUBLIC bool List_set_property(List list, size_t property, ptr_t value);


/**
 * Sorts a list.
 *
 * @param [in,out] list list to sort
 * @param [in] compare comparison function that returns a negative number, zero,
 *        or a positive number if the first argument is considered to be
 *        respectively less than, equal to, greater than the second (if @c NULL
 *        uses the subtraction operator on the @c #ptr_t::data component of each
 *        element)
 * @see #List_reverse
 * @note Errors that set @c errno to:
 *       - @c EPERM: List is being iterated.
 */
PUBLIC void List_sort(List list, int (*compare)(ptr_t, ptr_t));


/**
 * Converts a list to an array.
 *
 * @code
 * List_add(years, DATA(1986));
 * List_add(years, DATA(1999));
 * List_add(years, DATA(2001));
 * 
 * int* array = (int*) List_to_array(years, sizeof(int));
 * ...
 * free(array);
 * @endcode
 *
 * @param [in] list list to convert
 * @param [in] data_size size, in bytes, of the @c #ptr_t::data component of
 *        each element, or zero to use the @c #ptr_t::code component
 * @return new array with all elements or @c NULL on error (see note)
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Empty list.
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC void* List_to_array(List list, size_t data_size);


#endif
