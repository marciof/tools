#include <limits.h>
#include <stdlib.h>
#include <string.h>

#include "../test.h"
#include "../util.h"
#include "Array_List.h"
#include "Linked_List.h"
#include "List.h"


static size_t f1(void) {
    return 1;
}


static size_t f2(void) {
    return 2;
}


static size_t f3(void) {
    return 3;
}


/**
 * Comparison function to sort a list of integers in descending order.
 *
 * @param [in] x first integer
 * @param [in] y second integer
 * @return negative number, zero, or a positive number if the first element is
 *         considered to be respectively less than, equal to, or greater than
 *         the second
 */
static int numerically_descending(ptr_t x, ptr_t y) {
    if (x.data < y.data) {
        return 1;
    }
    else if (x.data > y.data) {
        return -1;
    }
    else {
        return 0;
    }
}


static void add_element_while_iterating(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    List_add(list, DATA("a"));
    assert_equals(errno, EPERM);
    assert_equals(List_length(list), 0);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void add_elements(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    const char* elements[] = {"a", "b", "c"};
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
        assert_equals(List_length(list), i + 1);
        assert_equals(errno, ENONE);
    }
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        assert_equals(List_get(list, i).data, elements[i]);
        assert_equals(errno, ENONE);
    }
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void check_iterator_has_next_on_empty_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_false(Iterator_has_next(iterator));
    assert_equals(errno, ENONE);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void check_iterator_has_next(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    List_add(list, DATA("a"));
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_true(Iterator_has_next(iterator));
    assert_equals(errno, ENONE);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void check_iterator_has_previous_on_empty_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_previous(iterator));
    assert_equals(errno, ENONE);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void check_iterator_has_previous(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    List_add(list, DATA("a"));
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_previous(iterator));
    assert_equals(errno, ENONE);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void convert_empty_list_to_array(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    void* array;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    array = List_to_array(list, sizeof(void*));
    assert_equals(errno, EINVAL);
    assert_null(array);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void convert_pointer_list_to_array(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    const char* elements[] = {"a", "e", "i", "o", "u"};
    const char** array;
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    array = (const char**) List_to_array(list, sizeof(char*));
    assert_equals(errno, ENONE);
    assert_not_null(array);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        assert_equals(array[i], elements[i]);
    }
    
    free((void*) array);
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void convert_char_list_to_array(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    char elements[] = {'a', 'e', 'i', 'o', 'u'};
    char* array;
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA((size_t) elements[i]));
        assert_equals(errno, ENONE);
    }
    
    array = (char*) List_to_array(list, sizeof(char));
    assert_equals(errno, ENONE);
    assert_not_null(array);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        assert_equals(array[i], elements[i]);
    }
    
    free((void*) array);
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void create_and_delete(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    assert_equals(List_length(list), 0);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void create_and_delete_iterator(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void create_and_delete_iterator_after_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void delete_null(UNUSED ptr_t implementation) {
    List_delete(NULL);
    assert_equals(errno, ENONE);
}


static void delete_null_iterator(UNUSED ptr_t implementation) {
    Iterator_delete(NULL);
    assert_equals(errno, ENONE);
}


static void delete_while_iterating(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    List_add(list, DATA("a"));
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, EPERM);
    assert_equals(List_length(list), 1);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void get_elements_from_empty_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    assert_equals(List_get(list, (size_t) -1).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(List_get(list, 0).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(List_get(list, 1).data, null.data);
    assert_equals(errno, EINVAL);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void get_elements_from_invalid_positions(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    const char* element = "a";
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    List_add(list, DATA(element));
    assert_equals(errno, ENONE);
    
    assert_equals(List_get(list, (size_t) -1).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(List_get(list, 0).data, element);
    assert_equals(errno, ENONE);
    
    assert_equals(List_get(list, 1).data, null.data);
    assert_equals(errno, EINVAL);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void insert_elements(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    const char* elements[] = {"a", "b", "c", "d"};
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    List_insert(list, DATA(elements[1]), 0);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), 1);
    
    List_insert(list, DATA(elements[3]), 1);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), 2);
    
    List_insert(list, DATA(elements[0]), 0);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), 3);
    
    List_insert(list, DATA(elements[2]), 2);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), 4);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        assert_equals(List_get(list, i).data, elements[i]);
        assert_equals(errno, ENONE);
    }
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void insert_elements_on_invalid_positions(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    const char* element = "Test";
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    List_insert(list, DATA(element), 0);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), 1);
    
    List_insert(list, DATA(element), (size_t) -1);
    assert_equals(errno, EINVAL);
    assert_equals(List_length(list), 1);
    
    List_insert(list, DATA(element), 2);
    assert_equals(errno, EINVAL);
    assert_equals(List_length(list), 1);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void iterate_backward(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    const char* elements[] = {"a", "b", "c"};
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_previous(iterator));
    assert_equals(errno, ENONE);
    
    assert_equals(Iterator_previous(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void iterate_backward_from_end(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    const char* elements[] = {"a", "b", "c"};
    ssize_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < (ssize_t) LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    Iterator_to_end(iterator);
    assert_equals(errno, ENONE);
    
    for (i = LENGTH_OF(elements) - 1; Iterator_has_previous(iterator); --i) {
        assert_equals(Iterator_previous(iterator).data, elements[i]);
        assert_equals(errno, ENONE);
    }
    
    assert_equals(Iterator_previous(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void iterate_backward_on_empty_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_previous(iterator));
    assert_equals(errno, ENONE);
    
    assert_equals(Iterator_previous(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void iterate_empty_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_previous(iterator));
    assert_equals(errno, ENONE);
    
    assert_equals(Iterator_next(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    assert_equals(Iterator_previous(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    assert_false(Iterator_has_previous(iterator));
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_equals(errno, ENONE);
    
    assert_equals(Iterator_previous(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    assert_equals(Iterator_next(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void iterate_forward(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    const char* elements[] = {"a", "b", "c"};
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    for (i = 0; Iterator_has_next(iterator); ++i) {
        assert_equals(Iterator_next(iterator).data, elements[i]);
        assert_equals(errno, ENONE);
    }
    
    assert_equals(Iterator_next(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void iterate_forward_from_start(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    const char* elements[] = {"a", "b", "c"};
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    Iterator_to_start(iterator);
    assert_equals(errno, ENONE);
    
    for (i = 0; Iterator_has_next(iterator); ++i) {
        assert_equals(Iterator_next(iterator).data, elements[i]);
        assert_equals(errno, ENONE);
    }
    
    assert_equals(Iterator_next(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void iterate_forward_on_empty_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_equals(errno, ENONE);
    
    assert_equals(Iterator_next(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void iterate_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    const char* elements[] = {"a", "b", "c"};
    ssize_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < (ssize_t) LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    for (i = 0; Iterator_has_next(iterator); ++i) {
        assert_equals(Iterator_next(iterator).data, elements[i]);
        assert_equals(errno, ENONE);
        
        assert_equals(Iterator_previous(iterator).data, elements[i]);
        assert_equals(errno, ENONE);
        
        assert_equals(Iterator_next(iterator).data, elements[i]);
        assert_equals(errno, ENONE);
    }
    
    assert_equals(Iterator_next(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    for (i = LENGTH_OF(elements) - 1; Iterator_has_previous(iterator); --i) {
        assert_equals(Iterator_previous(iterator).data, elements[i]);
        assert_equals(errno, ENONE);
        
        assert_equals(Iterator_next(iterator).data, elements[i]);
        assert_equals(errno, ENONE);
        
        assert_equals(Iterator_previous(iterator).data, elements[i]);
        assert_equals(errno, ENONE);
    }
    
    assert_equals(Iterator_previous(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void move_iterator_to_end_on_empty_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_false(Iterator_has_previous(iterator));
    
    Iterator_to_end(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_false(Iterator_has_previous(iterator));
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void move_iterator_to_start_on_empty_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_false(Iterator_has_previous(iterator));
    
    Iterator_to_start(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_false(Iterator_has_previous(iterator));
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void remove_element_while_iterating(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    List_add(list, DATA("a"));
    assert_equals(errno, ENONE);
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_equals(List_remove(list, 0).data, null.data);
    assert_equals(errno, EPERM);
    assert_equals(List_length(list), 1);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void remove_elements(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    const char* elements[] = {"a", "b", "c", "d"};
    ssize_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < (ssize_t) LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    assert_equals(List_remove(list, 0).data, elements[0]);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), 3);
    
    assert_equals(List_remove(list, 1).data, elements[2]);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), 2);
    
    assert_equals(List_remove(list, 1).data, elements[3]);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), 1);
    
    assert_equals(List_remove(list, 0).data, elements[1]);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), 0);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void remove_elements_from_empty_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    assert_equals(List_remove(list, (size_t) -1).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(List_remove(list, 0).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(List_remove(list, 1).data, null.data);
    assert_equals(errno, EINVAL);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void remove_elements_from_invalid_positions(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    const char* element = "a";
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    List_add(list, DATA(element));
    assert_equals(errno, ENONE);
    
    assert_equals(List_remove(list, (size_t) -1).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(List_remove(list, 1).data, null.data);
    assert_equals(errno, EINVAL);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void replace_elements_by_position(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    const char* elements[] = {"a", "b", "c"};
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        const char* element = elements[LENGTH_OF(elements) - i - 1];
        
        assert_equals(List_replace(list, DATA(element), i).data, elements[i]);
        assert_equals(errno, ENONE);
        assert_equals(List_get(list, i).data, element);
    }
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void replace_elements_by_position_on_empty_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    assert_equals(List_replace(list, DATA("a"), (size_t) -1).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(List_replace(list, DATA("a"), 0).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(List_replace(list, DATA("a"), 1).data, null.data);
    assert_equals(errno, EINVAL);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void replace_elements_by_position_on_invalid_positions(ptr_t impl) {
    List list = List_new((List_Implementation) impl.data);
    const char* element = "a";
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    List_add(list, DATA(element));
    assert_equals(errno, ENONE);
    
    assert_equals(List_replace(list, DATA("b"), (size_t) -1).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(List_replace(list, DATA("b"), 1).data, null.data);
    assert_equals(errno, EINVAL);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void reverse_list_while_iterating(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    const char* elements[] = {"a", "b", "c"};
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    List_reverse(list);
    assert_equals(errno, EPERM);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        assert_equals(List_get(list, i).data, elements[i]);
        assert_equals(errno, ENONE);
    }
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void reverse_list_with_even_length(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    const char* elements[] = {"a", "b", "c", "d"};
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    List_reverse(list);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), LENGTH_OF(elements));
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        const char* element = elements[LENGTH_OF(elements) - i - 1];
        assert_equals(List_get(list, i).data, element);
        assert_equals(errno, ENONE);
    }
    
    List_reverse(list);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), LENGTH_OF(elements));
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        assert_equals(List_get(list, i).data, elements[i]);
        assert_equals(errno, ENONE);
    }
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void reverse_list_with_odd_length(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    const char* elements[] = {"a", "b", "c"};
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    List_reverse(list);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), LENGTH_OF(elements));
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        const char* element = elements[LENGTH_OF(elements) - i - 1];
        assert_equals(List_get(list, i).data, element);
        assert_equals(errno, ENONE);
    }
    
    List_reverse(list);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), LENGTH_OF(elements));
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        assert_equals(List_get(list, i).data, elements[i]);
        assert_equals(errno, ENONE);
    }
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void reverse_empty_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    List_reverse(list);
    assert_equals(errno, ENONE);
    
    List_reverse(list);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void reverse_single_element_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    const char* element = "a";
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    List_add(list, DATA(element));
    assert_equals(errno, ENONE);
    
    List_reverse(list);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), 1);
    assert_equals(List_get(list, 0).data, element);
    
    List_reverse(list);
    assert_equals(errno, ENONE);
    assert_equals(List_length(list), 1);
    assert_equals(List_get(list, 0).data, element);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void sort_empty_list(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    List_sort(list, NULL);
    assert_equals(errno, ENONE);
    
    List_sort(list, numerically_descending);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void sort_list_while_iterating(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    Iterator iterator;
    const char* elements[] = {"b", "a", "c"};
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    iterator = List_iterator(list);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    List_sort(list, NULL);
    assert_equals(errno, EPERM);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        assert_equals(List_get(list, i).data, elements[i]);
        assert_equals(errno, ENONE);
    }
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void sort_list_with_even_length(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    size_t elements[] = {2, 1, 0, 1};
    size_t previous = 0;
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    List_sort(list, NULL);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        size_t current = (size_t) List_get(list, i).data;
        
        assert_true(previous <= current);
        previous = current;
    }
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void sort_list_with_odd_length(ptr_t implementation) {
    List list = List_new((List_Implementation) implementation.data);
    size_t elements[] = {1, 1, 2, 3, 0};
    size_t previous = 0;
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    List_sort(list, NULL);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        size_t current = (size_t) List_get(list, i).data;
        
        assert_true(previous <= current);
        previous = current;
    }
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void sort_list_with_even_length_using_custom_comparator(ptr_t impl) {
    List list = List_new((List_Implementation) impl.data);
    size_t elements[] = {2, 1, 0, 1};
    size_t previous = SIZE_MAX;
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    List_sort(list, numerically_descending);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        size_t current = (size_t) List_get(list, i).data;
        
        assert_true(previous >= current);
        previous = current;
    }
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void sort_list_with_odd_length_using_custom_comparator(ptr_t impl) {
    List list = List_new((List_Implementation) impl.data);
    size_t elements[] = {1, 1, 2, 3, 0};
    size_t previous = SIZE_MAX;
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    List_sort(list, numerically_descending);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        size_t current = (size_t) List_get(list, i).data;
        
        assert_true(previous >= current);
        previous = current;
    }
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void use_function_pointers_as_elements(ptr_t implementation) {
    typedef size_t (*Function)(void);
    
    List list = List_new((List_Implementation) implementation.data);
    Function elements[] = {f1, f2, f3};
    size_t expected[] = {1, 2, 3};
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    assert_equals(LENGTH_OF(elements), LENGTH_OF(expected));
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, CODE(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        Function f = (Function) List_get(list, i).code;
        
        assert_equals(f, elements[i]);
        assert_equals(f(), expected[i]);
    }
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static ptr_t get_Array_List(void) {
    return DATA(Array_List);
}

static ptr_t get_Linked_List(void) {
    return DATA(Linked_List);
}

struct Test_Parameter test_parameters[] = {
    {"Array_List", get_Array_List},
    {"Linked_List", get_Linked_List},
    {NULL, NULL}
};


Test tests[] = {
    /* List: */
    
    create_and_delete,
    delete_null,
    
    insert_elements,
    insert_elements_on_invalid_positions,
    add_elements,
    
    get_elements_from_empty_list,
    get_elements_from_invalid_positions,
    
    remove_elements,
    remove_elements_from_empty_list,
    remove_elements_from_invalid_positions,
    
    replace_elements_by_position,
    replace_elements_by_position_on_empty_list,
    replace_elements_by_position_on_invalid_positions,
    
    reverse_empty_list,
    reverse_single_element_list,
    reverse_list_with_odd_length,
    reverse_list_with_even_length,
    
    convert_empty_list_to_array,
    convert_pointer_list_to_array,
    convert_char_list_to_array,
    use_function_pointers_as_elements,
    
    sort_empty_list,
    sort_list_with_odd_length,
    sort_list_with_odd_length_using_custom_comparator,
    sort_list_with_even_length,
    sort_list_with_even_length_using_custom_comparator,
    
    /* List iterator: */
    
    create_and_delete_iterator,
    delete_null_iterator,
    create_and_delete_iterator_after_list,
    
    check_iterator_has_next_on_empty_list,
    check_iterator_has_previous_on_empty_list,
    check_iterator_has_next,
    check_iterator_has_previous,
    
    move_iterator_to_end_on_empty_list,
    move_iterator_to_start_on_empty_list,
    
    iterate_backward_on_empty_list,
    iterate_forward_on_empty_list,
    iterate_backward,
    iterate_forward,
    
    iterate_backward_from_end,
    iterate_forward_from_start,
    iterate_empty_list,
    iterate_list,
    
    delete_while_iterating,
    add_element_while_iterating,
    remove_element_while_iterating,
    reverse_list_while_iterating,
    sort_list_while_iterating,
    
    NULL
};
