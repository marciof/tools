#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "Array_List.h"


#define DEFAULT_INITIAL_CAPACITY ((size_t) 8)
#define INSERTION_SORT_THRESHOLD ((size_t) 12)


enum Array_Iterator_Direction {
    BACKWARD, FORWARD
};

enum Array_Iterator_Location {
    END, MIDDLE, START
};


typedef int (*Comparator)(intptr_t, intptr_t);


typedef struct _Array {
    intptr_t* array;
    size_t iterators;
    size_t length;
    size_t capacity;
} * Array;


typedef struct _Array_Iterator {
    Array list;
    size_t position;
    unsigned int direction : 1;
    unsigned int location : 2;
}* Array_Iterator;


static void insertion_sort(
    Array list,
    Comparator compare,
    size_t low,
    size_t high)
{
    for (size_t i = low + 1; i < high; ++i) {
        for (size_t j = i; j > low; --j) {
            if (compare(list->array[j], list->array[j - 1]) < 0) {
                intptr_t element = list->array[j];
                
                list->array[j] = list->array[j - 1];
                list->array[j - 1] = element;
            }
            else {
                break;
            }
        }
    }
}


static size_t lower(
    Array list,
    Comparator compare,
    size_t low,
    size_t high,
    size_t i)
{
    for (size_t length = high - low; length > 0;) {
        size_t half = length / 2;
        size_t middle = low + half;
        
        if (compare(list->array[middle], list->array[i]) < 0) {
            low = middle + 1;
            length = length - half -1;
        }
        else {
            length = half;
        }
    }
    
    return low;
}


static size_t upper(
    Array list,
    Comparator compare,
    size_t low,
    size_t high,
    size_t i)
{
    for (size_t length = high - low; length > 0;) {
        size_t half = length / 2;
        size_t middle = low + half;
        
        if (compare(list->array[i], list->array[middle]) < 0) {
            length = half;
        }
        else {
            low = middle + 1;
            length = length - half -1;
        }
    }
    
    return low;
}


static size_t gcd(size_t x, size_t y) {
    while (y != 0) {
        size_t temp = x % y;
        
        x = y;
        y = temp;
    }
    
    return x;
}


static void rotate(Array list, size_t low, size_t pivot, size_t high) {
    // Less sophisticated but costlier version:
    //
    // merge_reverse(list, low, pivot - 1);
    // merge_reverse(list, mid, high - 1);
    // merge_reverse(list, low, high - 1);
    //
    // static void merge_reverse(List list, size_t low, size_t high) {
    //     for (; low < high; ++low, --high) {
    //         intptr_t temp = list->array[low];
    //
    //         list->array[low] = list->array[high];
    //         list->array[high] = temp;
    //     }
    // }

    if ((low == pivot) || (pivot == high)) {
        return;
    }
    
    for (size_t n = gcd(high - low, pivot - low); n-- != 0;) {
        intptr_t element = list->array[low + n];
        size_t shift = pivot - low;
        size_t p1 = low + n;
        size_t p2 = low + n + shift;
        
        while (p2 != (low + n)) {
            list->array[p1] = list->array[p2];
            p1 = p2;
            
            if ((high - p2) > shift) {
                p2 += shift;
            }
            else {
                p2 = low + (shift - (high - p2));
            }
        }
        
        list->array[p1] = element;
    }
}


static void merge(
    Array list,
    Comparator compare,
    size_t low,
    size_t pivot,
    size_t high,
    size_t length_1,
    size_t length_2)
{
    size_t first_cut, second_cut, len_1, len_2;
    
    if ((length_1 == 0) || (length_2 == 0)) {
        return;
    }
    
    if ((length_1 + length_2) == 2) {
        if (compare(list->array[pivot], list->array[low]) < 0) {
            intptr_t element = list->array[pivot];
            
            list->array[pivot] = list->array[low];
            list->array[low] = element;
        }
        return;
    }
    
    if (length_1 > length_2) {
        len_1 = length_1 / 2;
        first_cut = low + len_1;
        second_cut = lower(list, compare, pivot, high, first_cut);
        len_2 = second_cut - pivot;
    }
    else {
        len_2 = length_2 / 2;
        second_cut = pivot + len_2;
        first_cut = upper(list, compare, low, pivot, second_cut);
        len_1 = first_cut - low;
    }
    
    size_t new_mid = first_cut + len_2;
    
    rotate(list, first_cut, pivot, second_cut);
    merge(list, compare, low, first_cut, new_mid, len_1, len_2);
    merge(list, compare, new_mid, second_cut, high,
        length_1 - len_1, length_2 - len_2);
}


/**
 * Change the list capacity.
 *
 * @param list list to modify
 * @param capacity new capacity
 * @param error error message, if any
 */
static void change_capacity(Array list, size_t capacity, Error* error) {
    if (capacity < list->length) {
        Error_errno(error, EINVAL);
        return;
    }
    
    intptr_t* array = (intptr_t*) realloc(
        list->array, capacity * sizeof(intptr_t));
    
    if (array == NULL) {
        Error_errno(error, ENOMEM);
        return;
    }
    
    list->array = array;
    list->capacity = capacity;
    Error_clear(error);
    return;
}


/**
 * Sort a list using the merge sort algorithm.
 *
 * @param list list to sort
 * @param compare comparison function that returns a negative number, zero,
 *        or a positive number if the first argument is considered to be
 *        respectively less than, equal to, or greater than the second
 * @param low index where to begin sorting
 * @param high index where to end sorting
 * @author Thomas Baudel
 * @see http://thomas.baudel.name/Visualisation/VisuTri/inplacestablesort.html
 */
static void merge_sort(
    Array list,
    Comparator compare,
    size_t low,
    size_t high)
{
    if ((high - low) < INSERTION_SORT_THRESHOLD) {
        insertion_sort(list, compare, low, high);
    }
    else {
        // Prevent possible overflow instead of using "(low + high) / 2".
        size_t middle = low + (high - low) / 2;
        
        merge_sort(list, compare, low, middle);
        merge_sort(list, compare, middle, high);
        merge(list, compare, low, middle, high, middle - low, high - middle);
    }
}


static void* create(Error* error) {
    Array list = (Array) malloc(sizeof(struct _Array));
    
    if (list == NULL) {
        Error_errno(error, ENOMEM);
        return NULL;
    }
    
    list->iterators = 0;
    list->length = 0;
    list->capacity = DEFAULT_INITIAL_CAPACITY;
    list->array = (intptr_t*) malloc(list->capacity * sizeof(intptr_t));
    
    if (list->array == NULL) {
        free(list);
        Error_errno(error, ENOMEM);
        return NULL;
    }
    
    Error_clear(error);
    return list;
}


static void destroy(void* l, Error* error) {
    Array list = (Array) l;
    
    if (list->iterators > 0) {
        Error_errno(error, EPERM);
        return;
    }
    
    free(list->array);
    memset(list, 0, sizeof(struct _Array));
    free(list);
    Error_clear(error);
}


static intptr_t get(void* l, size_t position, Error* error) {
    Array list = (Array) l;
    
    if (position >= list->length) {
        Error_errno(error, EINVAL);
        return 0;
    }
    
    Error_clear(error);
    return list->array[position];
}


static intptr_t get_property(void* l, size_t property, Error* error) {
    Array list = (Array) l;
    
    switch (property) {
    case ARRAY_LIST_CAPACITY:
        Error_clear(error);
        return list->capacity;
    default:
        Error_errno(error, EINVAL);
        return 0;
    }
}


static void insert(void* l, intptr_t element, size_t position, Error* error) {
    Array list = (Array) l;
    
    if (position > list->length) {
        Error_errno(error, EINVAL);
        return;
    }

    if ((list->length == SIZE_MAX) || (list->iterators > 0)) {
        Error_errno(error, EPERM);
        return;
    }
    
    if (list->length >= list->capacity) {
        change_capacity(list, (size_t) (list->capacity * 1.5 + 1), error);
        
        if (Error_has(error)) {
            return;
        }
    }
    
    if (position < list->length) {
        for (size_t i = list->length; i > position; --i) {
            list->array[i] = list->array[i - 1];
        }
    }
    
    ++list->length;
    list->array[position] = element;
    Error_clear(error);
}


static size_t length(void* l) {
    return ((Array) l)->length;
}


static intptr_t remove(void* l, size_t position, Error* error) {
    Array list = (Array) l;

    if (position >= list->length) {
        Error_errno(error, EINVAL);
        return 0;
    }

    if (list->iterators > 0) {
        Error_errno(error, EPERM);
        return 0;
    }
    
    --list->length;
    intptr_t element = list->array[position];
    
    if (position < list->length) {
        for (size_t i = position; i < list->length; ++i) {
            list->array[i] = list->array[i + 1];
        }
    }
    
    Error_clear(error);
    return element;
}


static intptr_t replace(
        void* l, intptr_t element, size_t position, Error* error) {

    Array list = (Array) l;

    if (position >= list->length) {
        Error_errno(error, EINVAL);
        return 0;
    }
    
    intptr_t previous_element = list->array[position];
    list->array[position] = element;
    
    Error_clear(error);
    return previous_element;
}


static void reverse(void* l, Error* error) {
    Array list = (Array) l;
    
    if (list->iterators > 0) {
        Error_errno(error, EPERM);
        return;
    }

    for (size_t left = 0; left < (list->length / 2); ++left) {
        intptr_t element = list->array[left];
        size_t right = list->length - left - 1;

        list->array[left] = list->array[right];
        list->array[right] = element;
    }

    Error_clear(error);
}


static void set_property(
        void* l, size_t property, intptr_t value, Error* error) {

    switch (property) {
    case ARRAY_LIST_CAPACITY:
        change_capacity((Array) l, (size_t) value, error);
        break;
    default:
        Error_errno(error, EINVAL);
        break;
    }
}


static void sort(void* l, Comparator compare, Error* error) {
    Array list = (Array) l;
    
    if (list->iterators > 0) {
        Error_errno(error, EPERM);
    }
    else {
        merge_sort(list, compare, 0, list->length);
        Error_clear(error);
    }
}


static void iterator_to_end(void* it) {
    Array_Iterator iterator = (Array_Iterator) it;
    
    iterator->position = (size_t) NULL;
    iterator->direction = BACKWARD;
    iterator->location = END;
}


static void iterator_to_start(void* it) {
    Array_Iterator iterator = (Array_Iterator) it;
    
    iterator->position = (size_t) NULL;
    iterator->direction = FORWARD;
    iterator->location = START;
}


static void* iterator_create(void* collection, Error* error) {
    Array list = (Array) collection;

    if (list->iterators == SIZE_MAX) {
        Error_errno(error, EPERM);
        return NULL;
    }
    
    Array_Iterator iterator = (Array_Iterator) malloc(
        sizeof(struct _Array_Iterator));
    
    if (iterator == NULL) {
        Error_errno(error, ENOMEM);
        return NULL;
    }
    
    iterator->list = list;
    ++list->iterators;

    iterator_to_start(iterator);
    Error_clear(error);
    return iterator;
}


static void iterator_destroy(void* it) {
    --((Array_Iterator) it)->list->iterators;
    memset(it, 0, sizeof(struct _Array_Iterator));
    free(it);
}


static bool iterator_has_next(void* it) {
    Array_Iterator iterator = (Array_Iterator) it;
    return (iterator->list->length > 0) && (iterator->location != END);
}


static bool iterator_has_previous(void* it) {
    Array_Iterator iterator = (Array_Iterator) it;
    return (iterator->list->length > 0) && (iterator->location != START);
}


static intptr_t iterator_next(void* it, Error* error) {
    Array_Iterator iterator = (Array_Iterator) it;

    if (!iterator_has_next(it)) {
        Error_errno(error, EPERM);
        return 0;
    }
    
    if (iterator->location == START) {
        iterator->position = 0;
        iterator->direction = FORWARD;
        iterator->location = MIDDLE;
    }
    else if (iterator->direction == BACKWARD) {
        iterator->direction = FORWARD;
    }
    else {
        ++iterator->position;
    }
    
    intptr_t element = iterator->list->array[iterator->position];
    
    if (iterator->position == (iterator->list->length - 1)) {
        iterator_to_end(iterator);
    }
    
    Error_clear(error);
    return element;
}


static intptr_t iterator_previous(void* it, Error* error) {
    Array_Iterator iterator = (Array_Iterator) it;

    if (!iterator_has_previous(it)) {
        Error_errno(error, EPERM);
        return 0;
    }
    
    if (iterator->location == END) {
        iterator->position = iterator->list->length - 1;
        iterator->direction = BACKWARD;
        iterator->location = MIDDLE;
    }
    else if (iterator->direction == FORWARD) {
        iterator->direction = BACKWARD;
    }
    else {
        --iterator->position;
    }
    
    intptr_t element = iterator->list->array[iterator->position];
    
    if (iterator->position == 0) {
        iterator_to_start(iterator);
    }
    
    Error_clear(error);
    return element;
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


const List_Impl Array_List = (List_Impl) &impl;
