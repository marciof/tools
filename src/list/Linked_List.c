#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "Linked_List.h"


enum Linked_Iterator_Direction {
    BACKWARD, FORWARD
};

enum Linked_Iterator_Location {
    END, MIDDLE, START
};


typedef struct _Linked_Element {
    struct _Linked_Element* next;
    struct _Linked_Element* previous;
    intptr_t value;
}* Linked_Element;


typedef struct _Linked {
    Linked_Element first;
    Linked_Element last;
    size_t length;
    size_t iterators;
}* Linked;


typedef struct _Linked_Iterator {
    Linked list;
    Linked_Element element;
    unsigned int direction : 1;
    unsigned int location : 2;
}* Linked_Iterator;


/**
 * Get an element from a list.
 *
 * @param list list from which to retrieve an element
 * @param position index of the element to retrieve
 * @return element at the given position
 */
static Linked_Element List_Element_get(Linked list, size_t position) {
    Linked_Element element;
    
    if (position <= (list->length / 2)) {
        // First half.
        element = list->first;
        
        for (size_t i = 0; i < position; ++i) {
            element = element->next;
        }
    }
    else {
        // Second half.
        element = list->last;
        
        for (size_t i = list->length - 1; i > position; --i) {
            element = element->previous;
        }
    }
    
    return element;
}


/**
 * Sort a list using the merge sort algorithm.
 *
 * @param list list to sort
 * @param compare comparison function that returns a negative number, zero,
 *        or a positive number if the first argument is considered to be
 *        respectively less than, equal to, or greater than the second
 * @author Simon Tatham
 * @see http://www.chiark.greenend.org.uk/~sgtatham/algorithms/listsort.html
 */
static void merge_sort(Linked list, int (*compare)(intptr_t, intptr_t)) {
    if (list->length <= 1) {
        return;
    }

    Linked_Element p, q;
    size_t merge_length, p_length, q_length;

    for (merge_length = 1; true; merge_length *= 2) {
        size_t merge_count = 0;
        
        p = list->first;
        list->first = list->last = NULL;
        
        while (p != NULL) {
            size_t i;
            
            // There's a merge to be done.
            ++merge_count;
            
            q = p;
            p_length = 0;
            
            for (i = 0; i < merge_length; ++i) {
                ++p_length;
                q = q->next;
                
                if (q == NULL) {
                    break;
                }
            }
            
            // If q isn't NULL, there are two lists to merge.
            q_length = merge_length;
            
            // Merge the two lists.
            while ((p_length > 0) || ((q_length > 0) && (q != NULL))) {
                Linked_Element element;
                
                // Decide whether the next element comes from p or q.
                if (p_length == 0) {
                    // p is empty, so the element must come from q.
                    element = q;
                    q = q->next;
                    --q_length;
                }
                else if ((q_length == 0) || (q == NULL)) {
                    // q is empty, so the element must come from p.
                    element = p;
                    p = p->next;
                    --p_length;
                }
                else if (compare(p->value, q->value) <= 0) {
                    // The first element of p is lower or equal, so the element
                    // must come from p.
                    element = p;
                    p = p->next;
                    --p_length;
                }
                else {
                    // The first element of q is lower, so the element must
                    // come from q.
                    element = q;
                    q = q->next;
                    --q_length;
                }
                
                // Add the next element to the merged list.
                if (list->last != NULL) {
                    list->last->next = element;
                }
                else {
                    list->first = element;
                }
                
                element->previous = list->last;
                list->last = element;
            }
            
            p = q;
        }
        
        list->last->next = NULL;
        
        if (merge_count <= 1) {
            break;
        }
    }
}


static void* create(Error* error) {
    Linked list = (Linked) malloc(sizeof(struct _Linked));
    
    if (list == NULL) {
        *error = strerror(ENOMEM);
        return NULL;
    }
    
    list->first = NULL;
    list->last = NULL;
    list->length = 0;
    list->iterators = 0;
    
    Error_clear(error);
    return list;
}


static void destroy(void* l, Error* error) {
    Linked list = (Linked) l;
    Linked_Element element = list->first;
    
    if (list->iterators > 0) {
        Error_set(error, strerror(EPERM));
        return;
    }
    
    while (element != NULL) {
        Linked_Element next = element->next;
        
        free(element);
        element = next;
    }

    memset(list, 0, sizeof(struct _Linked));
    free(list);
    Error_clear(error);
}


static intptr_t get(void* l, size_t position, Error* error) {
    Linked list = (Linked) l;
    
    if (position >= list->length) {
        *error = strerror(EINVAL);
        return 0;
    }
    
    Error_clear(error);
    return List_Element_get(list, position)->value;
}


static intptr_t get_property(void* l, size_t property, Error* error) {
    *error = strerror(EINVAL);
    return 0;
}


static void insert(void* l, intptr_t value, size_t position, Error* error) {
    Linked list = (Linked) l;

    if (position > list->length) {
        *error = strerror(EINVAL);
        return;
    }
    if ((list->length == SIZE_MAX) || (list->iterators > 0)) {
        *error = strerror(EPERM);
        return;
    }
    
    Linked_Element element = (Linked_Element) malloc(
        sizeof(struct _Linked_Element));
    
    if (element == NULL) {
        *error = strerror(ENOMEM);
        return;
    }
    
    if (position == 0) {
        element->next = list->first;
        element->previous = NULL;
        list->first = element;
        
        if (list->length == 0) {
            list->last = element;
        }
        else {
            element->next->previous = element;
        }
    }
    else if (position == list->length) {
        element->next = NULL;
        element->previous = list->last;
        
        list->last->next = element;
        list->last = element;
    }
    else {
        Linked_Element next = List_Element_get(list, position);
        
        element->next = next;
        element->previous = next->previous;
        
        next->previous->next = element;
        next->previous = element;
    }
    
    ++list->length;
    element->value = value;
    Error_clear(error);
}


static size_t length(void* l) {
    return ((Linked) l)->length;
}


static intptr_t remove(void* l, size_t position, Error* error) {
    Linked list = (Linked) l;

    if (position >= list->length) {
        *error = strerror(EINVAL);
        return 0;
    }
    if (list->iterators > 0) {
        *error = strerror(EPERM);
        return 0;
    }
    
    Linked_Element element = List_Element_get(list, position);
    intptr_t previous_value = element->value;
    
    if (position == 0) {
        list->first = element->next;
        
        if (list->length == 1) {
            list->last = NULL;
        }
        else {
            list->first->previous = NULL;
        }
    }
    else if (position == (list->length - 1)) {
        list->last = element->previous;
        list->last->next = NULL;
    }
    else {
        element->previous->next = element->next;
        element->next->previous = element->previous;
    }
    
    free(element);
    --list->length;
    
    Error_clear(error);
    return previous_value;
}


static intptr_t replace(
        void* l, intptr_t value, size_t position, Error* error) {

    Linked list = (Linked) l;

    if (position >= list->length) {
        *error = strerror(EINVAL);
        return 0;
    }
    
    Linked_Element element = List_Element_get(list, position);
    intptr_t previous_value = element->value;

    element->value = value;
    Error_clear(error);
    return previous_value;
}


static void reverse(void* l, Error* error) {
    Linked list = (Linked) l;
    
    if (list->iterators > 0) {
        *error = strerror(EPERM);
        return;
    }

    Linked_Element element = list->first;

    list->first = list->last;
    list->last = element;

    while (element != NULL) {
        Linked_Element next = element->next;

        element->next = element->previous;
        element->previous = next;

        element = next;
    }

    Error_clear(error);
}


static void set_property(
        void* l, size_t property, intptr_t value, Error* error) {

    *error = strerror(EINVAL);
}


static void sort(void* l, int (* compare)(intptr_t, intptr_t), Error* error) {
    Linked list = (Linked) l;
    
    if (list->iterators > 0) {
        *error = strerror(EPERM);
    }
    else {
        merge_sort(list, compare);
        Error_clear(error);
    }
}


static void iterator_to_end(void* it) {
    Linked_Iterator iterator = (Linked_Iterator) it;
    
    iterator->element = NULL;
    iterator->direction = BACKWARD;
    iterator->location = END;
}


static void iterator_to_start(void* it) {
    Linked_Iterator iterator = (Linked_Iterator) it;
    
    iterator->element = NULL;
    iterator->direction = FORWARD;
    iterator->location = START;
}


static void* iterator_create(void* collection, Error* error) {
    Linked list = (Linked) collection;

    if (list->iterators == SIZE_MAX) {
        *error = strerror(EPERM);
        return NULL;
    }
    
    Linked_Iterator iterator = (Linked_Iterator) malloc(
        sizeof(struct _Linked_Iterator));
    
    if (iterator == NULL) {
        *error = strerror(ENOMEM);
        return NULL;
    }
    
    iterator->list = list;
    ++list->iterators;

    iterator_to_start(iterator);
    Error_clear(error);
    return iterator;
}


static void iterator_destroy(void* it) {
    --((Linked_Iterator) it)->list->iterators;
    memset(it, 0, sizeof(struct _Linked_Iterator));
    free(it);
}


static bool iterator_has_next(void* it) {
    Linked_Iterator iterator = (Linked_Iterator) it;
    return (iterator->list->length > 0) && (iterator->location != END);
}


static bool iterator_has_previous(void* it) {
    Linked_Iterator iterator = (Linked_Iterator) it;
    return (iterator->list->length > 0) && (iterator->location != START);
}


static intptr_t iterator_next(void* it, Error* error) {
    Linked_Iterator iterator = (Linked_Iterator) it;

    if (!iterator_has_next(it)) {
        Error_set(error, strerror(EPERM));
        return 0;
    }
    
    if (iterator->location == START) {
        iterator->element = iterator->list->first;
        iterator->direction = FORWARD;
        iterator->location = MIDDLE;
    }
    else if (iterator->direction == BACKWARD) {
        iterator->direction = FORWARD;
    }
    else {
        iterator->element = iterator->element->next;
    }
    
    intptr_t value = iterator->element->value;
    
    if (iterator->element == iterator->list->last) {
        iterator_to_end(iterator);
    }
    
    Error_clear(error);
    return value;
}


static intptr_t iterator_previous(void* it, Error* error) {
    Linked_Iterator iterator = (Linked_Iterator) it;

    if (!iterator_has_previous(it)) {
        *error = strerror(EPERM);
        return 0;
    }
    
    if (iterator->location == END) {
        iterator->element = iterator->list->last;
        iterator->direction = BACKWARD;
        iterator->location = MIDDLE;
    }
    else if (iterator->direction == FORWARD) {
        iterator->direction = BACKWARD;
    }
    else {
        iterator->element = iterator->element->previous;
    }
    
    intptr_t value = iterator->element->value;
    
    if (iterator->element == iterator->list->first) {
        iterator_to_start(iterator);
    }
    
    Error_clear(error);
    return value;
}


static const struct _Iterator_Impl iterator_impl = {
    iterator_create,
    iterator_destroy,
    iterator_to_end,
    iterator_to_start,
    iterator_has_next,
    iterator_has_previous,
    iterator_next,
    iterator_previous
};


static const struct _List_Impl impl = {
    (Iterator_Impl) &iterator_impl,
    create,
    destroy,
    get,
    get_property,
    insert,
    length,
    remove,
    replace,
    reverse,
    set_property,
    sort
};


const List_Impl Linked_List = (List_Impl) &impl;
