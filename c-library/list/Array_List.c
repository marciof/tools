#include "../std/stdlib.h"
#include "../std/string.h"
#include "../types.h"
#include "Array_List.h"


#define DEFAULT_INITIAL_CAPACITY ((size_t) 8)
#define INSERTION_SORT_THRESHOLD ((size_t) 12)


enum Iterator_Direction {
    BACKWARD, FORWARD
};

enum Iterator_Location {
    END, MIDDLE, START
};


typedef int (*Comparator)(ptr_t, ptr_t);


typedef struct _List* List;

struct _List {
    ptr_t* array;
    size_t iterators;
    size_t length;
    size_t capacity;
};


typedef struct _Iterator* Iterator;

struct _Iterator {
    List list;
    size_t position;
    unsigned int direction : 1;
    unsigned int location : 2;
};


static void insertion_sort(
    List list,
    Comparator compare,
    size_t low,
    size_t high)
{
    size_t i, j;
    
    for (i = low + 1; i < high; ++i) {
        for (j = i; j > low; --j) {
            if (compare(list->array[j], list->array[j - 1]) < 0) {
                ptr_t element = list->array[j];
                
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
    List list,
    Comparator compare,
    size_t low,
    size_t high,
    size_t i)
{
    size_t length;
    
    for (length = high - low; length > 0;) {
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
    List list,
    Comparator compare,
    size_t low,
    size_t high,
    size_t i)
{
    size_t length;
    
    for (length = high - low; length > 0;) {
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


static void rotate(List list, size_t low, size_t pivot, size_t high) {
    /*
    Less sophisticated but costlier version:
    
    merge_reverse(list, low, pivot - 1);
    merge_reverse(list, mid, high - 1);
    merge_reverse(list, low, high - 1);
    
    static void merge_reverse(List list, size_t low, size_t high) {
        for (; low < high; ++low, --high) {
            ptr_t temp = list->array[low];
            
            list->array[low] = list->array[high];
            list->array[high] = temp;
        }
    }
    */
    
    size_t n;
    
    if ((low == pivot) || (pivot == high)) {
        return;
    }
    
    for (n = gcd(high - low, pivot - low); n-- != 0;) {
        ptr_t element = list->array[low + n];
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
    List list,
    Comparator compare,
    size_t low,
    size_t pivot,
    size_t high,
    size_t length_1,
    size_t length_2)
{
    size_t first_cut, second_cut, len_1, len_2, new_mid;
    
    if ((length_1 == 0) || (length_2 == 0)) {
        return;
    }
    
    if ((length_1 + length_2) == 2) {
        if (compare(list->array[pivot], list->array[low]) < 0) {
            ptr_t element = list->array[pivot];
            
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
    
    new_mid = first_cut + len_2;
    
    rotate(list, first_cut, pivot, second_cut);
    merge(list, compare, low, first_cut, new_mid, len_1, len_2);
    merge(list, compare, new_mid, second_cut, high,
        length_1 - len_1, length_2 - len_2);
}


/**
 * Changes the list capacity.
 *
 * @param [in,out] list list to modify
 * @param [in] capacity new capacity value
 * @return @c ENONE if the capacity was changed or an error code otherwise
 */
static int change_capacity(List list, size_t capacity) {
    ptr_t* array;
    
    if (capacity < list->length) {
        return EINVAL;
    }
    
    array = (ptr_t*) realloc(list->array, capacity * sizeof(ptr_t));
    
    if (array == NULL) {
        return ENOMEM;
    }
    
    list->array = array;
    list->capacity = capacity;
    return ENONE;
}


/**
 * Sorts a list using the merge sort algorithm.
 *
 * @param [in,out] list list to sort
 * @param [in] compare comparison function that returns a negative number, zero,
 *        or a positive number if the first argument is considered to be
 *        respectively less than, equal to, or greater than the second
 * @param [in] low index where to begin sorting
 * @param [in] high index where to end sorting
 * @author Thomas Baudel
 * @see http://thomas.baudel.name/Visualisation/VisuTri/inplacestablesort.html
 */
static void merge_sort(
    List list,
    Comparator compare,
    size_t low,
    size_t high)
{
    if ((high - low) < INSERTION_SORT_THRESHOLD) {
        insertion_sort(list, compare, low, high);
    }
    else {
        /* Prevent possible overflow instead of using "(low + high) / 2". */
        size_t middle = low + (high - low) / 2;
        
        merge_sort(list, compare, low, middle);
        merge_sort(list, compare, middle, high);
        merge(list, compare, low, middle, high, middle - low, high - middle);
    }
}


static void* create(int* error) {
    List list = (List) malloc(sizeof(struct _List));
    
    if (list == NULL) {
        *error = ENOMEM;
        return NULL;
    }
    
    list->iterators = 0;
    list->length = 0;
    list->capacity = DEFAULT_INITIAL_CAPACITY;
    list->array = (ptr_t*) malloc(list->capacity * sizeof(ptr_t));
    
    if (list->array == NULL) {
        free(list);
        *error = ENOMEM;
        return NULL;
    }
    
    *error = ENONE;
    return list;
}


static void destroy(int* error, void* l) {
    List list = (List) l;
    
    if (list->iterators > 0) {
        *error = EPERM;
        return;
    }
    
    free(list->array);
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
    return list->array[position];
}


static ptr_t get_property(int* error, void* l, size_t property) {
    List list = (List) l;
    
    switch (property) {
    case ARRAY_LIST_CAPACITY:
        *error = ENONE;
        return DATA(list->capacity);
    default:
        *error = EINVAL;
        return null;
    }
}


static void insert(int* error, void* l, ptr_t element, size_t position) {
    List list = (List) l;
    
    if (position > list->length) {
        *error = EINVAL;
        return;
    }
    if ((list->length == SIZE_MAX) || (list->iterators > 0)) {
        *error = EPERM;
        return;
    }
    
    if (list->length >= list->capacity) {
        *error = change_capacity(list, (size_t) (list->capacity * 1.5 + 1));
        
        if (*error != ENONE) {
            return;
        }
    }
    
    if (position < list->length) {
        size_t i;
        
        for (i = list->length; i > position; --i) {
            list->array[i] = list->array[i - 1];
        }
    }
    
    ++list->length;
    list->array[position] = element;
    *error = ENONE;
}


static size_t length(int* error, void* l) {
    *error = ENONE;
    return ((List) l)->length;
}


static ptr_t remove(int* error, void* l, size_t position) {
    List list = (List) l;
    ptr_t element;
    
    if (position >= list->length) {
        *error = EINVAL;
        return null;
    }
    if (list->iterators > 0) {
        *error = EPERM;
        return null;
    }
    
    --list->length;
    element = list->array[position];
    
    if (position < list->length) {
        size_t i;
        
        for (i = position; i < list->length; ++i) {
            list->array[i] = list->array[i + 1];
        }
    }
    
    *error = ENONE;
    return element;
}


static ptr_t replace(int* error, void* l, ptr_t element, size_t position) {
    List list = (List) l;
    ptr_t previous_element;
    
    if (position >= list->length) {
        *error = EINVAL;
        return null;
    }
    
    previous_element = list->array[position];
    list->array[position] = element;
    
    *error = ENONE;
    return previous_element;
}


static void reverse(int* error, void* l) {
    List list = (List) l;
    
    if (list->iterators > 0) {
        *error = EPERM;
    }
    else {
        size_t left;
        
        for (left = 0; left < (list->length / 2); ++left) {
            ptr_t element = list->array[left];
            size_t right = list->length - left - 1;
            
            list->array[left] = list->array[right];
            list->array[right] = element;
        }
        
        *error = ENONE;
    }
}


static void set_property(int* error, void* l, size_t property, ptr_t value) {
    switch (property) {
    case ARRAY_LIST_CAPACITY:
        *error = change_capacity((List) l, (size_t) value.data);
        break;
    default:
        *error = EINVAL;
        break;
    }
}


static void sort(int* error, void* l, Comparator compare) {
    List list = (List) l;
    
    if (list->iterators > 0) {
        *error = EPERM;
    }
    else {
        merge_sort(list, compare, 0, list->length);
        *error = ENONE;
    }
}


static void Iterator_to_end(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    
    iterator->position = (size_t) NULL;
    iterator->direction = BACKWARD;
    iterator->location = END;
    
    *error = ENONE;
}


static void Iterator_to_start(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    
    iterator->position = (size_t) NULL;
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
    ptr_t element;
    
    if (!Iterator_has_next(error, it)) {
        *error = EPERM;
        return null;
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
    
    element = iterator->list->array[iterator->position];
    
    if (iterator->position == (iterator->list->length - 1)) {
        Iterator_to_end(error, iterator);
    }
    
    *error = ENONE;
    return element;
}


static ptr_t Iterator_previous(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    ptr_t element;
    
    if (!Iterator_has_previous(error, it)) {
        *error = EPERM;
        return null;
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
    
    element = iterator->list->array[iterator->position];
    
    if (iterator->position == 0) {
        Iterator_to_start(error, iterator);
    }
    
    *error = ENONE;
    return element;
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


const List_Implementation Array_List = (List_Implementation) &implementation;
