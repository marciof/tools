#include "../std/stdlib.h"
#include "../std/string.h"
#include "../types.h"
#include "../util.h"
#include "Linked_List.h"


enum Iterator_Direction {
    BACKWARD, FORWARD
};

enum Iterator_Location {
    END, MIDDLE, START
};


typedef struct _List_Element* List_Element;

struct _List_Element {
    List_Element next;
    List_Element previous;
    ptr_t value;
};


typedef struct _List* List;

struct _List {
    List_Element first;
    List_Element last;
    size_t length;
    size_t iterators;
};


typedef struct _Iterator* Iterator;

struct _Iterator {
    List list;
    List_Element element;
    unsigned int direction : 1;
    unsigned int location : 2;
};


/**
 * Gets an element from a list.
 *
 * @param [in] list list from which to retrieve an element
 * @param [in] position index of the element to retrieve
 * @return element at the given position
 */
static List_Element List_Element_get(List list, size_t position) {
    List_Element element;
    
    if (position <= (list->length / 2)) {
        size_t i;
        
        /* First half. */
        element = list->first;
        
        for (i = 0; i < position; ++i) {
            element = element->next;
        }
    }
    else {
        ssize_t i;
        
        /* Second half. */
        element = list->last;
        
        for (i = list->length - 1; i > (ssize_t) position; --i) {
            element = element->previous;
        }
    }
    
    return element;
}


/**
 * Sorts a list using the merge sort algorithm.
 *
 * @param [in,out] list list to sort
 * @param [in] compare comparison function that returns a negative number, zero,
 *        or a positive number if the first argument is considered to be
 *        respectively less than, equal to, or greater than the second
 * @author Simon Tatham
 * @see http://www.chiark.greenend.org.uk/~sgtatham/algorithms/listsort.html
 */
static void merge_sort(List list, int (*compare)(ptr_t, ptr_t)) {
    List_Element p, q;
    size_t merge_length, p_length, q_length;
    
    if (list->length <= 1) {
        return;
    }
    
    for (merge_length = 1; true; merge_length *= 2) {
        size_t merge_count = 0;
        
        p = list->first;
        list->first = list->last = NULL;
        
        while (p != NULL) {
            size_t i;
            
            /* There's a merge to be done. */
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
            
            /* If q isn't NULL, there are two lists to merge. */
            q_length = merge_length;
            
            /* Merge the two lists. */
            while ((p_length > 0) || ((q_length > 0) && (q != NULL))) {
                List_Element element;
                
                /* Decide whether the next element comes from p or q. */
                if (p_length == 0) {
                    /* p is empty, so the element must come from q. */
                    element = q;
                    q = q->next;
                    --q_length;
                }
                else if ((q_length == 0) || (q == NULL)) {
                    /* q is empty, so the element must come from p. */
                    element = p;
                    p = p->next;
                    --p_length;
                }
                else if (compare(p->value, q->value) <= 0) {
                    /* The first element of p is lower or equal, so the element
                       must come from p. */
                    element = p;
                    p = p->next;
                    --p_length;
                }
                else {
                    /* The first element of q is lower, so the element must
                       come from q. */
                    element = q;
                    q = q->next;
                    --q_length;
                }
                
                /* Add the next element to the merged list. */
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


static void* create(int* error) {
    List list = (List) malloc(sizeof(struct _List));
    
    if (list == NULL) {
        *error = ENOMEM;
        return NULL;
    }
    
    list->first = NULL;
    list->last = NULL;
    list->length = 0;
    list->iterators = 0;
    
    *error = ENONE;
    return list;
}


static void destroy(int* error, void* l) {
    List list = (List) l;
    List_Element element = list->first;
    
    if (list->iterators > 0) {
        *error = EPERM;
        return;
    }
    
    while (element != NULL) {
        List_Element next = element->next;
        
        free(element);
        element = next;
    }
    
    memset(list, 0, sizeof(struct _List));
    free(list);
    *error = ENONE;
}


static ptr_t get(int* error, void* l, size_t position) {
    List list = (List) l;
    
    if (position >= list->length) {
        *error = EINVAL;
        return null;
    }
    
    *error = ENONE;
    return List_Element_get(list, position)->value;
}


static ptr_t get_property(int* error, UNUSED void* l, UNUSED size_t property) {
    *error = EINVAL;
    return null;
}


static void insert(int* error, void* l, ptr_t value, size_t position) {
    List list = (List) l;
    List_Element element;
    
    if (position > list->length) {
        *error = EINVAL;
        return;
    }
    if ((list->length == SIZE_MAX) || (list->iterators > 0)) {
        *error = EPERM;
        return;
    }
    
    element = (List_Element) malloc(sizeof(struct _List_Element));
    
    if (element == NULL) {
        *error = ENOMEM;
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
        List_Element next = List_Element_get(list, position);
        
        element->next = next;
        element->previous = next->previous;
        
        next->previous->next = element;
        next->previous = element;
    }
    
    ++list->length;
    element->value = value;
    *error = ENONE;
}


static size_t length(int* error, void* l) {
    *error = ENONE;
    return ((List) l)->length;
}


static ptr_t remove(int* error, void* l, size_t position) {
    List list = (List) l;
    List_Element element;
    ptr_t previous_value;
    
    if (position >= list->length) {
        *error = EINVAL;
        return null;
    }
    if (list->iterators > 0) {
        *error = EPERM;
        return null;
    }
    
    element = List_Element_get(list, position);
    previous_value = element->value;
    
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
    
    *error = ENONE;
    return previous_value;
}


static ptr_t replace(int* error, void* l, ptr_t value, size_t position) {
    List list = (List) l;
    List_Element element;
    ptr_t previous_value;
    
    if (position >= list->length) {
        *error = EINVAL;
        return null;
    }
    
    element = List_Element_get(list, position);
    previous_value = element->value;
    element->value = value;
    
    *error = ENONE;
    return previous_value;
}


static void reverse(int* error, void* l) {
    List list = (List) l;
    
    if (list->iterators > 0) {
        *error = EPERM;
    }
    else {
        List_Element element = list->first;
        
        list->first = list->last;
        list->last = element;
        
        while (element != NULL) {
            List_Element next = element->next;
            
            element->next = element->previous;
            element->previous = next;
            
            element = next;
        }
        
        *error = ENONE;
    }
}


static void set_property(
    int* error,
    UNUSED void* l,
    UNUSED size_t property,
    UNUSED ptr_t value)
{
    *error = EINVAL;
}


static void sort(int* error, void* l, int (*compare)(ptr_t, ptr_t)) {
    List list = (List) l;
    
    if (list->iterators > 0) {
        *error = EPERM;
    }
    else {
        merge_sort(list, compare);
        *error = ENONE;
    }
}


static void Iterator_to_end(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    
    iterator->element = NULL;
    iterator->direction = BACKWARD;
    iterator->location = END;
    
    *error = ENONE;
}


static void Iterator_to_start(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    
    iterator->element = NULL;
    iterator->direction = FORWARD;
    iterator->location = START;
    
    *error = ENONE;
}


static void* Iterator_create(int* error, void* collection) {
    List list = (List) collection;
    Iterator iterator;
    
    if (list->iterators == SIZE_MAX) {
        *error = EPERM;
        return NULL;
    }
    
    iterator = (Iterator) malloc(sizeof(struct _Iterator));
    
    if (iterator == NULL) {
        *error = ENOMEM;
        return NULL;
    }
    
    iterator->list = list;
    ++list->iterators;
    
    Iterator_to_start(error, iterator);
    return iterator;
}


static void Iterator_destroy(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    
    --iterator->list->iterators;
    memset(iterator, 0, sizeof(struct _Iterator));
    free(iterator);
    
    *error = ENONE;
}


static bool Iterator_has_next(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    
    *error = ENONE;
    return (iterator->list->length > 0) && (iterator->location != END);
}


static bool Iterator_has_previous(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    
    *error = ENONE;
    return (iterator->list->length > 0) && (iterator->location != START);
}


static ptr_t Iterator_next(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    ptr_t value;
    
    if (!Iterator_has_next(error, it)) {
        *error = EPERM;
        return null;
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
    
    value = iterator->element->value;
    
    if (iterator->element == iterator->list->last) {
        Iterator_to_end(error, iterator);
    }
    
    *error = ENONE;
    return value;
}


static ptr_t Iterator_previous(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    ptr_t value;
    
    if (!Iterator_has_previous(error, it)) {
        *error = EPERM;
        return null;
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
    
    value = iterator->element->value;
    
    if (iterator->element == iterator->list->first) {
        Iterator_to_start(error, iterator);
    }
    
    *error = ENONE;
    return value;
}


static const struct _Iterator_Implementation iterator_implementation = {
    Iterator_create,
    Iterator_destroy,
    Iterator_to_end,
    Iterator_to_start,
    Iterator_has_next,
    Iterator_has_previous,
    Iterator_next,
    Iterator_previous
};


static const struct _List_Implementation implementation = {
    (Iterator_Implementation) &iterator_implementation,
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


const List_Implementation Linked_List = (List_Implementation) &implementation;
