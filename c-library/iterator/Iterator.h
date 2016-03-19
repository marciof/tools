#ifndef __EON__LIBRARY__ITERATOR__ITERATOR__
#define __EON__LIBRARY__ITERATOR__ITERATOR__


/**
 * @file
 * @brief Iterator interface
 *
 * Defines the interface to manipulate iterator instances.
 */


#include "../util.h"
#include "Iterator_Implementation.h"


/**
 * Iterator instance.
 */
typedef struct _Iterator* Iterator;


/**
 * Deletes an iterator.
 *
 * @param [in,out] iterator iterator to delete, unless @c NULL
 * @see #Iterator_new
 */
PUBLIC void Iterator_delete(Iterator iterator);


/**
 * Checks if an iterator has more elements when going forward.
 *
 * @param [in] iterator iterator to check for more elements
 * @return @c true if the iterator has more elements or @c false otherwise
 * @see #Iterator_has_previous
 * @see #Iterator_next
 */
PUBLIC bool Iterator_has_next(Iterator iterator);


/**
 * Checks if an iterator has more elements when going backward.
 *
 * @param [in] iterator iterator to check for more elements
 * @return @c true if the iterator has more elements or @c false otherwise
 * @see #Iterator_has_next
 * @see #Iterator_previous
 */
PUBLIC bool Iterator_has_previous(Iterator iterator);


/**
 * Creates an iterator.
 *
 * @param [in] impl iterator implementation to use
 * @param [in] collection collection to create an iterator for
 * @return new iterator for the given collection or @c NULL on error (see note)
 * @see #Iterator_delete
 * @see #List_iterator
 * @see #Map_keys_iterator
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 *       - @c EPERM: Maximum number (@c SIZE_MAX) of iterators reached.
 */
PUBLIC Iterator Iterator_new(Iterator_Implementation impl, void* collection);


/**
 * Gets the next element from an iterator and moves it forward.
 *
 * @param [in,out] iterator iterator to retrieve the next element from
 * @return next element or @c #null on error (see note)
 * @see #Iterator_has_next
 * @see #Iterator_previous
 * @note Errors that set @c errno to:
 *       - @c EPERM: No more next elements.
 */
PUBLIC ptr_t Iterator_next(Iterator iterator);


/**
 * Gets the previous element from an iterator and moves it backward.
 *
 * @param [in,out] iterator iterator to retrieve the previous element from
 * @return previous element or @c #null on error (see note)
 * @see #Iterator_has_previous
 * @see #Iterator_next
 * @note Errors that set @c errno to:
 *       - @c EPERM: No more previous elements.
 */
PUBLIC ptr_t Iterator_previous(Iterator iterator);


/**
 * Moves an iterator to the end.
 *
 * @param [in,out] iterator iterator to move to the end of its collection
 * @see #Iterator_to_start
 */
PUBLIC void Iterator_to_end(Iterator iterator);


/**
 * Moves an iterator to the start.
 *
 * @param [in,out] iterator iterator to move to the start of its collection
 * @see #Iterator_to_end
 */
PUBLIC void Iterator_to_start(Iterator iterator);


#endif
