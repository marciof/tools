#ifndef __EON__LIBRARY__LIST__LINKED_LIST__
#define __EON__LIBRARY__LIST__LINKED_LIST__


/**
 * @file
 * @brief Linked list implementation
 *
 * Contains a linked list implementation using a list interface.
 */


#include "../util.h"
#include "List_Implementation.h"


/**
 * Doubly linked linear list implementation.
 *
 * The sorting algorithm is stable and is O(n log n) in time and O(1) in memory.
 *
 * @see #List_new
 */
PUBLIC const List_Implementation Linked_List;


#endif
